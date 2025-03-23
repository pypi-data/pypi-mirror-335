#!/bin/bash
CSV_FILE="nodes.csv"

# Ensure the CSV file exists
if [[ ! -f "$CSV_FILE" ]]; then
  echo "Error: CSV file '$CSV_FILE' not found." >&2
  exit 1
fi

# Check if CSV file ends with a newline (to avoid missing the last line)
if [[ -n "$(tail -c 1 "$CSV_FILE")" ]]; then
  echo "Error: CSV file '$CSV_FILE' does not end with a newline." >&2
  exit 1
fi

# Read all node addresses from the CSV file.
# Each line should be in the format: username@host|machine_class
nodes=()
while IFS='|' read -r node mclass; do
  # Skip if the node field is empty
  if [[ -n "$node" ]]; then
    nodes+=("$node")
  fi
done < "$CSV_FILE"

# If no nodes are found, exit
if [ ${#nodes[@]} -eq 0 ]; then
  echo "No nodes found in '$CSV_FILE'. Nothing to do."
  exit 0
fi

# Create a comma-separated list for pdsh
nodes_list=$(IFS=,; echo "${nodes[*]}")

echo "Killing tmux sessions on nodes: $nodes_list"
pdsh -w "$nodes_list" "
  tmux kill-session -t origin_session 2>/dev/null;
  tmux kill-session -t middle_session 2>/dev/null;
  tmux kill-session -t client_session 2>/dev/null;
"

echo "Tmux sessions killed (if they existed) on the listed nodes."
