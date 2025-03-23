# PyLogr

A beautiful and colorful logging utility for Python that provides a modern, terminal-friendly logging experience with rich formatting and status indicators.

## Features

- 🎨 Beautiful colored output with ANSI color codes
- ⏰ Timestamp for each log entry
- 🏷️ Customizable application name
- 🔄 58+ predefined status types with appropriate colors
- 📝 Clean and modern formatting
- 🎯 Easy to use API

## Installation

```bash
pip install pylogr
```

## Quick Start

```python
from pylogr import PyLogr

# Create a logger instance with your app name
logger = PyLogr("MyApp")

# Log messages with different statuses
logger.log("Application started", PyLogr.STARTED)
logger.log("Task completed successfully", PyLogr.COMPLETED)
logger.log("Warning: Resource running low", PyLogr.WARNING)
logger.log("Critical error occurred", PyLogr.CRITICAL)
```

## Available Status Types

PyLogr comes with 58+ predefined status types, each with its own color:

### Basic Statuses
- SUCCESS
- ERROR
- INFO
- WARNING
- DEBUG
- CRITICAL
- DEFAULT

### Process Statuses
- COMPLETED
- PENDING
- FAILED
- STARTED
- STOPPED
- RUNNING
- QUEUED
- CANCELLED
- TIMEOUT
- RETRYING

### System Statuses
- MAINTENANCE
- UPGRADED
- DOWNGRADED
- CONNECTED
- DISCONNECTED
- SYNCED
- DESYNCED

### State Statuses
- ENABLED
- DISABLED
- ACTIVE
- INACTIVE
- ONLINE
- OFFLINE
- BUSY
- IDLE

### Security Statuses
- LOCKED
- UNLOCKED
- VERIFIED
- UNVERIFIED
- AUTHORIZED
- UNAUTHORIZED

And many more! Each status is color-coded for easy visual identification.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 