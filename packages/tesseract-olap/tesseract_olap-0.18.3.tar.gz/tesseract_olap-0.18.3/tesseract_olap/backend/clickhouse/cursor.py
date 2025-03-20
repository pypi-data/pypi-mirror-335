import logging
import queue
from collections import defaultdict
from concurrent import futures

from clickhouse_driver.dbapi import Error as ClickhouseDbapiError
from clickhouse_driver.errors import Error as ClickhouseError

from tesseract_olap.exceptions.backend import BackendValidationError
from tesseract_olap.schema import CubeTraverser, InlineTable, Measure, SchemaTraverser

from .dialect import TypedCursor, TypedDictCursor
from .sqlbuild import membercountquery_sql

logger = logging.getLogger(__name__)


def fetch_membercount(
    cursor_queue: "queue.Queue[TypedDictCursor]",
    cube: "CubeTraverser",
) -> tuple[str, dict[str, int]]:
    """Threaded function to request member count for all levels in cube."""
    cursor = cursor_queue.get()

    try:
        query, meta = membercountquery_sql(cube)

        cursor.reset_cursor()
        for table in meta.tables:
            cursor.set_inline_table(table)
        cursor.execute(query.get_sql())

        result: dict[str, int] = cursor.fetchone() or {"_empty": 0}
        return cube.name, result

    finally:
        cursor_queue.put(cursor)


def inyect_members_count(schema: "SchemaTraverser", cursor_list: list[TypedDictCursor]) -> None:
    """Update the `count` property on all Levels in the Schema with the number of members, as returned by the provided cursors from the ClickhouseBackend.

    The process runs in parallel using as many cursors are passed as argument.
    """
    count_total = sum(
        len(hie.level_map)
        for cube in schema.cube_map.values()
        for dim in cube.dimensions
        for hie in dim.hierarchies
    )
    executor = futures.ThreadPoolExecutor(max_workers=len(cursor_list))

    cursor_queue = queue.Queue(maxsize=len(cursor_list))
    for cursor in cursor_list:
        cursor_queue.put(cursor)

    try:
        # Run queries in parallel
        promises = tuple(
            executor.submit(fetch_membercount, cursor_queue, cube)
            for cube in sorted(schema.cube_map.values(), key=lambda cube: cube.name)
        )

        # Wait for the results and process them
        count_progress = 0
        for future in futures.as_completed(promises, timeout=6 * len(promises)):
            try:
                result = future.result()
            except (ClickhouseDbapiError, ClickhouseError) as exc:
                log = "Error counting cube members (%s): %s"
                message, stack = str(exc).split("Stack trace:", maxsplit=1)
                code, message = message.split("\n", maxsplit=1)
                logger.debug(log, code.strip(". "), message.strip())
                continue

            cube_name, members = result

            count_progress += len(members)
            logger.debug(
                "Updated member count for cube %r (%d/%d)",
                cube_name,
                count_progress,
                count_total,
                extra=members,
            )

            cube = schema.get_cube(cube_name)
            for level in cube.levels:
                count = members.get(level.name, 0)
                if count == 0:
                    logger.warning(
                        "Level(cube=%r, name=%r) returned 0 members",
                        cube.name,
                        level.name,
                    )
                level.count = count

    except KeyboardInterrupt:
        logger.debug("Interrupted by the user")

    finally:
        # Ensure children threads are terminated
        executor.shutdown(wait=False)


def validate_schema_tables(schema: "SchemaTraverser", cursor: "TypedCursor") -> None:
    """Validate the tables and columns declared in the Schema entities against the Backend."""
    schema_tables = unwrap_tables(schema)
    logger.debug("Tables to validate: %d", len(schema_tables))

    sql = (
        "SELECT table, groupArray(name) AS columns "
        "FROM system.columns "
        "WHERE table IN splitByChar(',', %(tables)s) "
        "GROUP BY table"
    )
    cursor.execute(sql, {"tables": ",".join(schema_tables.keys())})
    observed_tables = {table: set(columns) for table, columns in (cursor.fetchall() or [])}

    if schema_tables != observed_tables:
        reasons = []

        for table, columns in schema_tables.items():
            if table not in observed_tables:
                reasons.append(
                    f"- Table '{table}' is defined in Schema but not available in Backend",
                )
                continue

            difference = columns.difference(observed_tables[table])
            if difference:
                reasons.append(
                    f"- Schema references columns {difference} in table '{table}', but not available in Backend",
                )

        if reasons:
            message = (
                "Mismatch between columns defined in the Schema and available in ClickhouseBackend:\n"
                + "\n".join(reasons)
            )
            raise BackendValidationError(message)


def unwrap_tables(self: SchemaTraverser) -> dict[str, set[str]]:
    """Extract the {table: column[]} data from all entities in the schema."""
    tables: dict[str, set[str]] = defaultdict(set)

    for cube in self.cube_map.values():
        table = cube.table
        if isinstance(table, InlineTable):
            continue

        # Index fact tables
        tables[table.name].update(
            (
                item.key_column
                for measure in cube.measures
                for item in measure.and_submeasures()
                if isinstance(item, Measure)
            ),
            (dimension.foreign_key for dimension in cube.dimensions),
        )

        for hierarchy in cube.hierarchies:
            table = hierarchy.table
            if table is None or isinstance(table, InlineTable):
                continue

            # Index dimension tables
            tables[table.name].update(
                (
                    item
                    for level in hierarchy.levels
                    for item in (level.key_column, *level.name_column_map.values())
                ),
                (
                    item
                    for propty in hierarchy.properties
                    for item in propty.key_column_map.values()
                ),
            )

    return dict(tables)
