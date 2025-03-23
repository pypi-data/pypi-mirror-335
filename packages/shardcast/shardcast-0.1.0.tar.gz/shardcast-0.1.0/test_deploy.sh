#!/bin/bash
# Each line in nodes.csv should be in the format, see nodes_example.csv:
# username@host|machine_class

CSV_FILE="nodes.csv"

ORIGIN_NODE_PORT=8001
MIDDLE_NODE_PORT=8001

# check if the CSV file exists
if [[ ! -f "$CSV_FILE" ]]; then
  echo "Error: CSV file '$CSV_FILE' not found, please ensure the file exists" >&2
  exit 1
fi

# check if the CSV file ends with a newline, otherwise last machine in file might be disgarded
if [[ -n "$(tail -c 1 "$CSV_FILE")" ]]; then
  echo "Error: CSV file '$CSV_FILE' does not end with a newline." >&2
  exit 1
fi

# data dir paths on each node, those will be created if they don't exist
ORIGIN_DATA_DIR="/tmp/shardcast_test/origin_data"
MIDDLE_DATA_DIR="/tmp/shardcast_test/middle_node_1"
CLIENT_DATA_DIR="/tmp/shardcast_test/client_data"

# initialize arrays for each machine class
origin_nodes=()
middle_nodes=()
client_nodes=()

# read and sort nodes from the CSV file
while IFS='|' read -r node mclass; do
  # Skip lines with missing fields.
  if [[ -z "$node" || -z "$mclass" ]]; then
    continue
  fi

  case "$mclass" in
    origin)
      origin_nodes+=("$node")
      ;;
    middle_node)
      middle_nodes+=("$node")
      ;;
    client)
      client_nodes+=("$node")
      ;;
    *)
      echo "Warning: Unknown machine class '$mclass' for node $node. Skipping." >&2
      ;;
  esac
done < "$CSV_FILE"

middle_nodes_with_ports=()
for node in "${middle_nodes[@]}"; do
  middle_nodes_with_ports+=("${node}:${MIDDLE_NODE_PORT}")
done

# # debug lines (optional)
# echo "middle_nodes: ${middle_nodes[@]}"
# echo "middle_nodes_with_ports: ${middle_nodes_with_ports[@]}"

# declare commands for each machine type
CMD_ORIGIN="~/.local/bin/uv run examples/example_usage.py --mode origin --data-dir $ORIGIN_DATA_DIR --port $ORIGIN_NODE_PORT --file-path /tmp/shardcast_test_1742251533/test_file.bin --log-level DEBUG"
CMD_MIDDLE_NODE="~/.local/bin/uv run examples/example_usage.py --mode middle --data-dir $MIDDLE_DATA_DIR --upstream \"${origin_nodes}:${ORIGIN_NODE_PORT}\" --port $MIDDLE_NODE_PORT"
CMD_CLIENT="~/.local/bin/uv run examples/example_usage.py --mode client --data-dir $CLIENT_DATA_DIR --servers \"$(IFS=,; echo "${middle_nodes_with_ports[*]}")\""

# ensure there is exactly one origin node
if [[ ${#origin_nodes[@]} -eq 0 ]]; then
  echo "Error: No origin node found in '$CSV_FILE'. Exiting." >&2
  exit 1
elif [[ ${#origin_nodes[@]} -gt 1 ]]; then
  echo "Error: More than one origin node found in '$CSV_FILE'. There should be exactly one." >&2
  exit 1
fi

# warn if there are no middle or client nodes
if [[ ${#middle_nodes[@]} -eq 0 ]]; then
  echo "Warning: No middle nodes found in '$CSV_FILE'." >&2
fi

if [[ ${#client_nodes[@]} -eq 0 ]]; then
  echo "Warning: No client nodes found in '$CSV_FILE'." >&2
fi

# helper function to join array elements with commas
join_by() {
  local IFS="$1"; shift; echo "$*";
}

# deploy exactly one origin node
origin_node="${origin_nodes[0]}"
echo "creating data directory on origin node: $origin_node"
pdsh -w "$origin_node" "mkdir -p $ORIGIN_DATA_DIR"
echo "Deploying origin script on $origin_node in a tmux session"
pdsh -w "$origin_node" "tmux new-session -d -s origin_session 'cd ~/shardcast && $CMD_ORIGIN; exec bash'"

echo --------------------------

# deploy middle nodes if any
if [[ ${#middle_nodes[@]} -gt 0 ]]; then
  middle_list=$(join_by , "${middle_nodes[@]}")
  echo "Creating data directories on middle nodes: $middle_list"
  pdsh -w "$middle_list" "mkdir -p $MIDDLE_DATA_DIR"

  echo "deploying middle node script on nodes: $middle_list in tmux sessions"
  pdsh -w "$middle_list" "tmux new-session -d -s middle_session 'cd ~/shardcast && $CMD_MIDDLE_NODE; exec bash'"
fi

echo --------------------------

# deploy client nodes if any
if [[ ${#client_nodes[@]} -gt 0 ]]; then
  client_list=$(join_by , "${client_nodes[@]}")
  echo "creating data directories on client nodes: $client_list"
  pdsh -w "$client_list" "mkdir -p $CLIENT_DATA_DIR"

  echo "deploying client node script on nodes: $client_list in tmux sessions"
  pdsh -w "$client_list" "tmux new-session -d -s client_session 'cd ~/shardcast && $CMD_CLIENT; exec bash'"
fi
