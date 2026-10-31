
import { describe, test, expect } from "vitest";
import { checkout } from "./app.js";

describe("Checkout", () => {
    test("calculates the checkout total", () => {
        const items = [
            { price: 100 },
            { price: 200 }
        ];

        expect(checkout(items)).toBe(300);
    });
});
