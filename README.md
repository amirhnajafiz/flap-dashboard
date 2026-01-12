# FLAK Dashboard

## Phase 1

- A single entity will read the file in chunks (10 MB).
- It passes the chunk of type bytes to reader workers.

## Phase 2

- A reader worker listens on a channel for input chunks.
- Once a chunk is received, it parses the bytes into lines of strings.
- For each line, it forms a data packet, which contains a key and payload.
- The data packet is sent to the reader-reductor distributer.

## Phase 3

- The distributer is a single entity that redirects a data packet to a reductor based on packet key.

## Phase 4

- The reductor worker listens on a channel for input lines.
- It stores the logs based on the given timestamp in batches (200).
- Once the batch is full, it starts the reduction process to group the logs.
- Once the data is reducted, it passes the data packet to the reductor-writer distributer.

## Phase 5

- The distributer is a single entiry that redirects a data packet to a reductor based on it's chunk index.
