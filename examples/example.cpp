#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <algorithm>
#include <stdexcept>

namespace util {

// Truncates a UTF-8 string to fit within the given byte size,
// ensuring the result remains valid UTF-8.
std::string_view truncate_utf8(std::string_view input, size_t byte_size) {
    if (byte_size >= input.length()) {
        return input;
    }

    int32_t index = static_cast<int32_t>(byte_size);
    const auto *data = reinterpret_cast<const uint8_t *>(input.data());

    // Walk backwards to find a valid UTF-8 boundary
    while (index > 0 && (data[index] & 0xC0) == 0x80) {
        --index;
    }

    return input.substr(0, static_cast<size_t>(index));
}

template <typename T>
class LRUCache {
public:
    explicit LRUCache(size_t capacity) : capacity_(capacity) {}

    bool contains(const std::string &key) const {
        return entries_.find(key) != entries_.end();
    }

    void insert(const std::string &key, T value) {
        if (entries_.size() >= capacity_) {
            evict_oldest();
        }
        entries_[key] = std::make_unique<T>(std::move(value));
        access_order_.push_back(key);
    }

    const T *get(const std::string &key) {
        auto it = entries_.find(key);
        if (it == entries_.end()) {
            return nullptr;
        }
        // Move to back of access order
        auto pos = std::find(access_order_.begin(), access_order_.end(), key);
        if (pos != access_order_.end()) {
            access_order_.erase(pos);
            access_order_.push_back(key);
        }
        return it->second.get();
    }

private:
    size_t capacity_;
    std::unordered_map<std::string, std::unique_ptr<T>> entries_;
    std::vector<std::string> access_order_;

    void evict_oldest() {
        if (!access_order_.empty()) {
            entries_.erase(access_order_.front());
            access_order_.erase(access_order_.begin());
        }
    }
};

} // namespace util
