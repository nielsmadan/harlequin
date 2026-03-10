import Foundation

/// A generic result cache with time-based expiration.
///
/// Stores computed values and automatically invalidates entries
/// older than the specified `ttl` (time-to-live) interval.
public class ExpiringCache<Key: Hashable, Value> {
    private struct Entry {
        let value: Value
        let timestamp: Date
    }

    private var storage: [Key: Entry] = [:]
    private let ttl: TimeInterval
    private let lock = NSLock()

    /// Creates a new cache with the given time-to-live in seconds.
    /// - Parameter ttl: Expiration interval. Default is 300 seconds.
    public init(ttl: TimeInterval = 300.0) {
        precondition(ttl > 0, "TTL must be positive")
        self.ttl = ttl
    }

    /// Retrieves a cached value, or computes and stores it if missing or expired.
    @discardableResult
    public func value(
        forKey key: Key,
        compute: () throws -> Value
    ) rethrows -> Value {
        lock.lock()
        defer { lock.unlock() }

        if let entry = storage[key] {
            let age = Date().timeIntervalSince(entry.timestamp)
            if age < ttl {
                return entry.value
            }
        }

        let newValue = try compute()
        storage[key] = Entry(value: newValue, timestamp: Date())
        return newValue
    }

    /// Removes all expired entries from the cache.
    public func purgeExpired() {
        lock.lock()
        defer { lock.unlock() }

        let now = Date()
        storage = storage.filter { _, entry in
            now.timeIntervalSince(entry.timestamp) < ttl
        }
    }

    /// The number of currently cached (possibly expired) entries.
    public var count: Int { storage.count }
}

extension ExpiringCache: CustomStringConvertible {
    public var description: String {
        "ExpiringCache(\(count) entries, ttl: \(ttl)s)"
    }
}
