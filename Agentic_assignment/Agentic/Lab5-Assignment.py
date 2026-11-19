
"""
LAB 5: MCP-STYLE CONNECTOR — MINI INTEGRATION SERVER

ORIGINAL PRACTICAL:
1. MCP Server and MCP Client
2. Capability discovery
3. read_file resource
4. query_db tool using SQLite
5. call_api mock API
6. Caller permission and SELECT-only SQL validation

ASSIGNMENT 1:
1. Add fourth capability: list_files
2. Discover capability dynamically
3. Call it without hard-coding its name in MCPClient

ASSIGNMENT 2:
1. Restrict read_file to /safe/
2. Reject paths outside the safe directory
3. Return structured security errors
4. Test path traversal and unauthorized paths

Run:
    python Lab5-Assignment.py
"""

import sqlite3
import posixpath


# ============================================================
# PART 1: SET UP SQLITE DATABASE
# ============================================================

conn = sqlite3.connect(":memory:")

conn.execute(
    "CREATE TABLE signups (event TEXT, count INTEGER)"
)

conn.executemany(
    "INSERT INTO signups VALUES (?, ?)",
    [
        ("AI Club Talk", 12),
        ("Hackathon Kickoff", 9),
        ("Robotics Demo", 15)
    ]
)

conn.commit()


# ============================================================
# PART 2: MOCK FILES AND API
# ============================================================

# Assignment 2: Files are stored inside the safe directory.
SAFE_DIRECTORY = "/safe/"

MOCK_FILES = {
    "/safe/README.md":
        "Agentic AI Systems - mini MCP server demo.",

    "/safe/project.txt":
        "This is a sample project file."
}

MOCK_API = {
    "events_today": [
        "AI Club Talk",
        "Robotics Demo"
    ]
}


# ============================================================
# PART 3: CAPABILITY MANIFEST
# ============================================================

CAPABILITIES = [

    {
        "name": "read_file",
        "kind": "resource",
        "input": {"path": "str"},
        "output": {"content": "str"}
    },

    {
        "name": "query_db",
        "kind": "tool",
        "input": {"sql": "str"},
        "output": {"rows": "list"}
    },

    {
        "name": "call_api",
        "kind": "tool",
        "input": {"endpoint": "str"},
        "output": {"data": "any"}
    },

    # Assignment 1: Fourth discoverable capability
    {
        "name": "list_files",
        "kind": "resource",
        "input": {},
        "output": {"files": "list"}
    }

]


# ============================================================
# PART 4: PERMISSIONS
# ============================================================

ALLOWED_CALLERS = {
    "planning_agent"
}


# ============================================================
# PART 5: MCP SERVER
# ============================================================

class MCPServer:

    def list_capabilities(self):

        return CAPABILITIES

    # --------------------------------------------------------
    # Original capability 1: read_file
    # Assignment 2: Safe directory restriction
    # --------------------------------------------------------

    def read_file(self, path):

        # Reject invalid path types.
        if not isinstance(path, str) or not path:

            return {
                "error": {
                    "code": "INVALID_PATH",
                    "message": "A valid file path is required.",
                    "path": str(path)
                }
            }

        # Normalize path to prevent traversal attacks.
        normalized_path = posixpath.normpath(path)

        # Check original and normalized paths.
        if (
            not path.startswith(SAFE_DIRECTORY)
            or not normalized_path.startswith(SAFE_DIRECTORY)
            or ".." in path.split("/")
        ):

            return {
                "error": {
                    "code": "PATH_OUTSIDE_SAFE_DIRECTORY",
                    "message": (
                        "Access denied. Files can only be read "
                        "from the /safe/ directory."
                    ),
                    "path": path
                }
            }

        # Check whether the file exists.
        if normalized_path not in MOCK_FILES:

            return {
                "error": {
                    "code": "FILE_NOT_FOUND",
                    "message": "File does not exist.",
                    "path": normalized_path
                }
            }

        return {
            "content": MOCK_FILES[normalized_path]
        }

    # --------------------------------------------------------
    # Original capability 2: query_db
    # --------------------------------------------------------

    def query_db(self, sql, caller):

        # Check caller permission.
        if caller not in ALLOWED_CALLERS:

            return {
                "error": (
                    f"caller '{caller}' is not permitted "
                    "to use query_db"
                )
            }

        # Allow only SELECT statements.
        if not sql.strip().upper().startswith("SELECT"):

            return {
                "error": (
                    "only SELECT statements are permitted "
                    "through this tool"
                )
            }

        try:

            cur = conn.execute(sql)

            return {
                "rows": cur.fetchall()
            }

        except sqlite3.Error as error:

            return {
                "error": f"Database error: {error}"
            }

    # --------------------------------------------------------
    # Original capability 3: call_api
    # --------------------------------------------------------

    def call_api(self, endpoint):

        if endpoint not in MOCK_API:

            return {
                "error": f"unknown endpoint: {endpoint}"
            }

        return {
            "data": MOCK_API[endpoint]
        }

    # --------------------------------------------------------
    # Assignment 1: Fourth capability - list_files
    # --------------------------------------------------------

    def list_files(self):

        """
        Return files available inside the declared safe directory.
        """

        files = [
            path
            for path in MOCK_FILES
            if path.startswith(SAFE_DIRECTORY)
        ]

        return {
            "files": files
        }


# ============================================================
# PART 6: MCP CLIENT
# ============================================================

class MCPClient:

    def __init__(self, server, caller_name):

        self.server = server
        self.caller_name = caller_name

    def discover(self):

        return self.server.list_capabilities()

    def call(self, capability_name, **kwargs):

        # Discover all capabilities dynamically.
        manifest = {
            capability["name"]: capability
            for capability in self.discover()
        }

        # Reject unknown capabilities.
        if capability_name not in manifest:

            raise ValueError(
                f"unknown capability: {capability_name}"
            )

        # Dynamically get the server method.
        method = getattr(
            self.server,
            capability_name
        )

        # Pass caller identity for database queries.
        if capability_name == "query_db":

            return method(
                caller=self.caller_name,
                **kwargs
            )

        # All other capabilities are called dynamically.
        return method(**kwargs)


# ============================================================
# PART 7: ORIGINAL PRACTICAL
# ============================================================

def original_practical(server, client):

    print("\n" + "=" * 70)
    print("ORIGINAL PRACTICAL: MCP-STYLE CONNECTOR")
    print("=" * 70)

    # Capability discovery
    print("\n=== Capability discovery ===")

    for capability in client.discover():

        print(
            f" {capability['name']} "
            f"({capability['kind']}) "
            f"input={capability['input']} "
            f"output={capability['output']}"
        )

    # Call 1: Read file
    print("\n=== Call 1: read_file (resource) ===")

    print(
        client.call(
            "read_file",
            path="/safe/README.md"
        )
    )

    # Call 2: Query database
    print(
        "\n=== Call 2: query_db "
        "(tool, permitted caller, SELECT only) ==="
    )

    print(
        client.call(
            "query_db",
            sql="SELECT event, count FROM signups"
        )
    )

    # Call 3: Call API
    print("\n=== Call 3: call_api (tool) ===")

    print(
        client.call(
            "call_api",
            endpoint="events_today"
        )
    )

    # Rejection: DELETE statement
    print(
        "\n=== Rejection path: disallowed statement ==="
    )

    print(
        client.call(
            "query_db",
            sql="DELETE FROM signups"
        )
    )

    # Rejection: Unauthorized caller
    print(
        "\n=== Rejection path: disallowed caller ==="
    )

    other_client = MCPClient(
        server,
        caller_name="unregistered_agent"
    )

    print(
        other_client.call(
            "query_db",
            sql="SELECT * FROM signups"
        )
    )


# ============================================================
# PART 8: ASSIGNMENT 1 — ADD FOURTH CAPABILITY
# ============================================================

def assignment_1(client):

    print("\n" + "=" * 70)
    print("ASSIGNMENT 1: FOURTH DISCOVERABLE CAPABILITY")
    print("=" * 70)

    # Discover the new capability.
    print("\n--- Discover all capabilities ---")

    discovered = client.discover()

    for capability in discovered:

        print(
            f"{capability['name']} "
            f"({capability['kind']})"
        )

    # Verify list_files is discoverable.
    capability_names = [
        capability["name"]
        for capability in discovered
    ]

    discovered_successfully = (
        "list_files" in capability_names
    )

    print(
        "\nlist_files discovered:",
        discovered_successfully
    )

    # Call the new capability dynamically.
    print("\n--- Call list_files dynamically ---")

    result = client.call("list_files")

    print(result)

    call_successful = (
        "files" in result
        and len(result["files"]) > 0
    )

    print(
        "\nlist_files call successful:",
        call_successful
    )

    if discovered_successfully and call_successful:

        print("\nASSIGNMENT 1: PASSED")

    else:

        print("\nASSIGNMENT 1: FAILED")


# ============================================================
# PART 9: ASSIGNMENT 2 — SAFE DIRECTORY RESTRICTION
# ============================================================

def assignment_2(client):

    print("\n" + "=" * 70)
    print("ASSIGNMENT 2: SAFE DIRECTORY RESTRICTION")
    print("=" * 70)

    # Test 1: Read an allowed file.
    print("\n--- Test 1: Allowed safe file ---")

    safe_result = client.call(
        "read_file",
        path="/safe/README.md"
    )

    print(safe_result)

    safe_passed = (
        "content" in safe_result
    )

    print("Safe file access successful:", safe_passed)

    # Test 2: Attempt to read outside safe directory.
    print("\n--- Test 2: Unauthorized file access ---")

    outside_result = client.call(
        "read_file",
        path="/private/secret.txt"
    )

    print(outside_result)

    outside_blocked = (
        "error" in outside_result
        and outside_result["error"]["code"]
        == "PATH_OUTSIDE_SAFE_DIRECTORY"
    )

    print(
        "Outside directory access blocked:",
        outside_blocked
    )

    # Test 3: Path traversal attack.
    print("\n--- Test 3: Path traversal attack ---")

    traversal_result = client.call(
        "read_file",
        path="/safe/../private/secret.txt"
    )

    print(traversal_result)

    traversal_blocked = (
        "error" in traversal_result
        and traversal_result["error"]["code"]
        == "PATH_OUTSIDE_SAFE_DIRECTORY"
    )

    print(
        "Path traversal attack blocked:",
        traversal_blocked
    )

    # Final validation.
    print("\n--- Security validation ---")

    print("Allowed file read:", safe_passed)

    print("Unauthorized path rejected:", outside_blocked)

    print("Path traversal rejected:", traversal_blocked)

    if safe_passed and outside_blocked and traversal_blocked:

        print("\nASSIGNMENT 2: PASSED")

    else:

        print("\nASSIGNMENT 2: FAILED")


# ============================================================
# PART 10: MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print("*" * 70)
    print("LAB 5: MCP-STYLE CONNECTOR — MINI INTEGRATION SERVER")
    print("*" * 70)

    server = MCPServer()

    client = MCPClient(
        server,
        caller_name="planning_agent"
    )

    # Run original practical.
    original_practical(server, client)

    # Run Assignment 1.
    assignment_1(client)

    # Run Assignment 2.
    assignment_2(client)

    print("\n" + "=" * 70)
    print("LAB 5 EXECUTION COMPLETED")
    print("=" * 70)

    conn.close()
