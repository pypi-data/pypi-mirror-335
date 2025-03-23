from datetime import datetime

class Colors:
    WHITE = "\u001b[37m"
    BLACK = "\u001b[30m"
    
    RED = "\033[38;2;255;85;85m"
    GREEN = "\033[38;2;85;255;85m"
    BLUE = "\033[38;2;85;85;255m"
    YELLOW = "\033[38;2;255;255;85m"
    
    MAGENTA = "\033[38;2;255;85;255m"
    BRIGHT_MAGENTA = "\033[38;2;255;128;255m"
    LIGHT_CORAL = "\033[38;2;255;128;128m"
    PINK = "\033[38;2;255;128;255m"
    ORANGE = "\033[38;2;255;170;85m"
    LIGHT_BLUE = "\033[38;2;128;255;255m"
    CYAN = "\033[38;2;85;255;255m"
    PURPLE = "\033[38;2;170;85;255m"
    GRAY = "\033[38;2;170;170;170m"
    
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"

class PyLogr:
    # Original statuses
    SUCCESS = "success"
    VALID = "valid"
    ERROR = "error"
    INFO = "info"
    INVALID = "invalid"
    WARNING = "warning"
    DEBUG = "debug"
    CRITICAL = "critical"
    DEFAULT = "default"

    # New statuses
    COMPLETED = "completed"
    PENDING = "pending"
    FAILED = "failed"
    STARTED = "started"
    STOPPED = "stopped"
    RUNNING = "running"
    QUEUED = "queued"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    RETRYING = "retrying"
    SKIPPED = "skipped"
    PASSED = "passed"
    BLOCKED = "blocked"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"
    STABLE = "stable"
    UNSTABLE = "unstable"
    MAINTENANCE = "maintenance"
    UPGRADED = "upgraded"
    DOWNGRADED = "downgraded"
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    SYNCED = "synced"
    DESYNCED = "desynced"
    ENABLED = "enabled"
    DISABLED = "disabled"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    VERIFIED = "verified"
    UNVERIFIED = "unverified"
    AUTHORIZED = "authorized"
    UNAUTHORIZED = "unauthorized"
    COMPATIBLE = "compatible"
    INCOMPATIBLE = "incompatible"
    OPTIMIZED = "optimized"
    DEGRADED = "degraded"
    RESTORED = "restored"
    BACKED_UP = "backed_up"
    RESTARTED = "restarted"
    SHUTDOWN = "shutdown"
    INITIALIZED = "initialized"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    RESUMED = "resumed"

    def __init__(self, app_name: str = "PyLogr"):
        self.app_name = app_name

    def log(self, message: str, status: str = DEFAULT) -> None:
        status_colors = {
            # Original status colors
            PyLogr.SUCCESS: Colors.GREEN,
            PyLogr.VALID: Colors.GREEN,
            PyLogr.ERROR: Colors.RED,
            PyLogr.INFO: Colors.LIGHT_BLUE,
            PyLogr.INVALID: Colors.LIGHT_CORAL,
            PyLogr.WARNING: Colors.YELLOW,
            PyLogr.DEBUG: Colors.CYAN,
            PyLogr.CRITICAL: Colors.PURPLE,
            PyLogr.DEFAULT: Colors.WHITE,
            
            # New status colors
            PyLogr.COMPLETED: Colors.GREEN,
            PyLogr.PENDING: Colors.YELLOW,
            PyLogr.FAILED: Colors.RED,
            PyLogr.STARTED: Colors.LIGHT_BLUE,
            PyLogr.STOPPED: Colors.GRAY,
            PyLogr.RUNNING: Colors.CYAN,
            PyLogr.QUEUED: Colors.ORANGE,
            PyLogr.CANCELLED: Colors.LIGHT_CORAL,
            PyLogr.TIMEOUT: Colors.RED,
            PyLogr.RETRYING: Colors.YELLOW,
            PyLogr.SKIPPED: Colors.GRAY,
            PyLogr.PASSED: Colors.GREEN,
            PyLogr.BLOCKED: Colors.PURPLE,
            PyLogr.DEPRECATED: Colors.ORANGE,
            PyLogr.EXPERIMENTAL: Colors.MAGENTA,
            PyLogr.STABLE: Colors.GREEN,
            PyLogr.UNSTABLE: Colors.YELLOW,
            PyLogr.MAINTENANCE: Colors.BLUE,
            PyLogr.UPGRADED: Colors.GREEN,
            PyLogr.DOWNGRADED: Colors.YELLOW,
            PyLogr.CONNECTED: Colors.GREEN,
            PyLogr.DISCONNECTED: Colors.RED,
            PyLogr.SYNCED: Colors.GREEN,
            PyLogr.DESYNCED: Colors.RED,
            PyLogr.ENABLED: Colors.GREEN,
            PyLogr.DISABLED: Colors.GRAY,
            PyLogr.ACTIVE: Colors.GREEN,
            PyLogr.INACTIVE: Colors.GRAY,
            PyLogr.ONLINE: Colors.GREEN,
            PyLogr.OFFLINE: Colors.RED,
            PyLogr.BUSY: Colors.YELLOW,
            PyLogr.IDLE: Colors.GRAY,
            PyLogr.LOCKED: Colors.RED,
            PyLogr.UNLOCKED: Colors.GREEN,
            PyLogr.VERIFIED: Colors.GREEN,
            PyLogr.UNVERIFIED: Colors.YELLOW,
            PyLogr.AUTHORIZED: Colors.GREEN,
            PyLogr.UNAUTHORIZED: Colors.RED,
            PyLogr.COMPATIBLE: Colors.GREEN,
            PyLogr.INCOMPATIBLE: Colors.RED,
            PyLogr.OPTIMIZED: Colors.GREEN,
            PyLogr.DEGRADED: Colors.YELLOW,
            PyLogr.RESTORED: Colors.GREEN,
            PyLogr.BACKED_UP: Colors.GREEN,
            PyLogr.RESTARTED: Colors.LIGHT_BLUE,
            PyLogr.SHUTDOWN: Colors.GRAY,
            PyLogr.INITIALIZED: Colors.GREEN,
            PyLogr.TERMINATED: Colors.RED,
            PyLogr.SUSPENDED: Colors.YELLOW,
            PyLogr.RESUMED: Colors.GREEN
        }

        color = status_colors.get(status, status_colors[PyLogr.DEFAULT])

        timestamp = datetime.now().strftime('%H:%M:%S')
        
        app_name = f"{Colors.BOLD}{Colors.MAGENTA}{self.app_name}{Colors.RESET}"
        timestamp_part = f"{Colors.DIM}{Colors.BRIGHT_MAGENTA}{timestamp}{Colors.RESET}"
        status_badge = f"{Colors.PINK}[{Colors.BOLD}{color}{status.upper()}{Colors.RESET}{Colors.PINK}]"
        
        print(f"{Colors.PINK}╭─{Colors.RESET} {app_name} {Colors.PINK}─{Colors.RESET} {timestamp_part} {Colors.PINK}─{Colors.RESET} {status_badge} {Colors.PINK}─{Colors.RESET} {color}{message}{Colors.RESET}")