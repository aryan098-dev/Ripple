export function calculateTotal(items) {
    if (!Array.isArray(items)) {
        throw new TypeError("Items must be an array");
    }

    return items.reduce(
        (total, item) => total + item.price,
        0
    );
}