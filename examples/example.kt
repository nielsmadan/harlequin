package collections

/**
 * Builds a new read-only [List] by populating a [MutableList] using
 * the given [builderAction] and returning a read-only list.
 */
@SinceKotlin("1.6")
@Suppress("LEAKED_IN_PLACE_LAMBDA")
public inline fun <E> buildList(
    @BuilderInference builderAction: MutableList<E>.() -> Unit
): List<E> {
    contract { callsInPlace(builderAction, InvocationKind.EXACTLY_ONCE) }
    return buildListInternal(builderAction)
}

internal fun <T> List<T>.optimizeReadOnlyList() = when (size) {
    0 -> emptyList()
    1 -> listOf(this[0])
    else -> this
}

/**
 * Binary search for a nullable comparable element.
 * Returns the index if found, or -(insertion point) - 1.
 */
public fun <T : Comparable<T>> List<T?>.binarySearch(
    element: T?,
    fromIndex: Int = 0,
    toIndex: Int = size
): Int {
    rangeCheck(size, fromIndex, toIndex)

    var low = fromIndex
    var high = toIndex - 1

    while (low <= high) {
        val mid = (low + high).ushr(1)
        val midVal = get(mid)
        val cmp = compareValues(midVal, element)

        when {
            cmp < 0 -> low = mid + 1
            cmp > 0 -> high = mid - 1
            else -> return mid
        }
    }
    return -(low + 1)
}

data class SearchResult<out T>(
    val value: T,
    val index: Int,
    val exact: Boolean
) {
    override fun toString(): String =
        "SearchResult(value=$value, index=$index, exact=$exact)"
}

sealed class Ordering {
    object Ascending : Ordering()
    object Descending : Ordering()
    data class Custom(val comparator: Comparator<*>) : Ordering()
}
