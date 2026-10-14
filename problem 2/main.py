import math
import random
import time
import matplotlib.pyplot as plt

def distance(p1, p2):
    """Return Euclidean distance between two points."""
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

def brute_force_closest_pair(points):
    """Find closest pair using brute force."""

    if len(points) < 2:
        return None, None, float("inf")

    min_distance = float("inf")
    closest_p1 = None
    closest_p2 = None

    for i in range(len(points)):
        for j in range(i + 1, len(points)):

            d = distance(points[i], points[j])

            if d < min_distance:
                min_distance = d
                closest_p1 = points[i]
                closest_p2 = points[j]

    return closest_p1, closest_p2, min_distance



def divide_and_conquer_closest_pair(points):
    """
    Find closest pair using the O(N log N)
    divide-and-conquer algorithm.
    """

    if len(points) < 2:
        return None, None, float("inf")

    px = sorted(points, key=lambda p: (p[0], p[1]))
    py = sorted(points, key=lambda p: (p[1], p[0]))

    def solve(px, py):

        n = len(px)

        if n <= 3:
            return brute_force_closest_pair(px)

        mid = n // 2

        qx = px[:mid]
        rx = px[mid:]

        mid_x = px[mid][0]

        left_counts = {}

        for point in qx:
            left_counts[point] = left_counts.get(point, 0) + 1

        qy = []
        ry = []

        for point in py:
            if left_counts.get(point, 0) > 0:
                qy.append(point)
                left_counts[point] -= 1
            else:
                ry.append(point)

        left_p1, left_p2, left_distance = solve(qx, qy)
        right_p1, right_p2, right_distance = solve(rx, ry)

        if left_distance <= right_distance:
            best_p1 = left_p1
            best_p2 = left_p2
            d = left_distance
        else:
            best_p1 = right_p1
            best_p2 = right_p2
            d = right_distance

        strip = [
            point
            for point in py
            if abs(point[0] - mid_x) < d
        ]

        # In 2D closest-pair geometry, only the next
        # few y-neighbours need to be checked.
        for i in range(len(strip)):

            for j in range(i + 1, min(i + 8, len(strip))):

                if strip[j][1] - strip[i][1] >= d:
                    break

                current_distance = distance(strip[i], strip[j])

                if current_distance < d:
                    d = current_distance
                    best_p1 = strip[i]
                    best_p2 = strip[j]

        return best_p1, best_p2, d

    return solve(px, py)

def run_corner_case_tests():

    test_cases = {
        "Duplicate Points": [
            (1, 1),
            (5, 5),
            (1, 1),
            (10, 10)
        ],

        "Same X Coordinate": [
            (5, 1),
            (5, 8),
            (5, 3),
            (5, 20)
        ],

        "Same Y Coordinate": [
            (1, 5),
            (8, 5),
            (3, 5),
            (20, 5)
        ],

        "Collinear Points": [
            (0, 0),
            (2, 2),
            (4, 4),
            (6, 6),
            (8, 8)
        ],

        "Exactly Two Points": [
            (1, 1),
            (4, 5)
        ]
    }

    print("\n========== CORNER CASE TESTS ==========")

    for name, test_points in test_cases.items():

        _, _, bf_distance = brute_force_closest_pair(test_points)

        _, _, dc_distance = divide_and_conquer_closest_pair(
            test_points
        )

        print(f"\n{name}")
        print("Points:", test_points)

        print(
            f"Brute Force Distance:       "
            f"{bf_distance:.6f}"
        )

        print(
            f"Divide & Conquer Distance:  "
            f"{dc_distance:.6f}"
        )

        if math.isclose(
            bf_distance,
            dc_distance,
            rel_tol=1e-9,
            abs_tol=1e-12
        ):
            print("Result: PASS")
        else:
            print("Result: FAIL")



def visualize_closest_pair(
    points,
    bf_p1,
    bf_p2,
    dc_p1,
    dc_p2,
    min_distance
):

    sorted_points = sorted(
        points,
        key=lambda p: (p[0], p[1])
    )

    mid = len(sorted_points) // 2
    mid_x = sorted_points[mid][0]

    x_values = [p[0] for p in points]
    y_values = [p[1] for p in points]

    plt.figure(figsize=(10, 7))

    plt.scatter(
        x_values,
        y_values,
        label="Points",
        zorder=3
    )

    plt.plot(
        [bf_p1[0], bf_p2[0]],
        [bf_p1[1], bf_p2[1]],
        linewidth=4,
        label="Brute Force Closest Pair",
        zorder=4
    )

    plt.plot(
        [dc_p1[0], dc_p2[0]],
        [dc_p1[1], dc_p2[1]],
        linestyle="--",
        linewidth=2,
        label="Divide & Conquer Closest Pair",
        zorder=5
    )

    plt.scatter(
        [dc_p1[0], dc_p2[0]],
        [dc_p1[1], dc_p2[1]],
        s=130,
        zorder=6
    )

    plt.axvline(
        x=mid_x,
        linestyle="--",
        linewidth=2,
        label="Top-Level Dividing Line"
    )

    plt.axvspan(
        mid_x - min_distance,
        mid_x + min_distance,
        alpha=0.15,
        label="Top-Level Strip (width = 2d)"
    )

    plt.annotate(
        str(dc_p1),
        dc_p1,
        xytext=(-65, 12),
        textcoords="offset points"
    )

    plt.annotate(
        str(dc_p2),
        dc_p2,
        xytext=(10, -22),
        textcoords="offset points"
    )

    plt.title(
        "Closest Pair - Brute Force vs Divide & Conquer\n"
        f"Minimum Distance = {min_distance:.6f}"
    )

    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.show()



def performance_analysis():

    sizes = [100, 500, 1000, 2000, 4000]

    brute_times = []
    divide_times = []

    print("\n========== PERFORMANCE ANALYSIS ==========")

    print(
        f"{'N':<10}"
        f"{'Brute Force (ms)':<22}"
        f"{'Divide & Conquer (ms)':<25}"
        f"Status"
    )

    for n in sizes:

        test_points = [
            (
                random.randint(-1_000_000, 1_000_000),
                random.randint(-1_000_000, 1_000_000)
            )
            for _ in range(n)
        ]


        start = time.perf_counter()

        _, _, bf_distance = brute_force_closest_pair(
            test_points
        )

        bf_time = (
            time.perf_counter() - start
        ) * 1000

       
        start = time.perf_counter()

        _, _, dc_distance = divide_and_conquer_closest_pair(
            test_points
        )

        dc_time = (
            time.perf_counter() - start
        ) * 1000

        brute_times.append(bf_time)
        divide_times.append(dc_time)

        if math.isclose(
            bf_distance,
            dc_distance,
            rel_tol=1e-9,
            abs_tol=1e-12
        ):
            status = "PASS"
        else:
            status = "FAIL"

        print(
            f"{n:<10}"
            f"{bf_time:<22.6f}"
            f"{dc_time:<25.6f}"
            f"{status}"
        )

    plt.figure(figsize=(9, 6))

    plt.plot(
        sizes,
        brute_times,
        marker="o",
        label="Brute Force O(N²)"
    )

    plt.plot(
        sizes,
        divide_times,
        marker="o",
        label="Divide & Conquer O(N log N)"
    )

    plt.title("Running Time vs Input Size")

    plt.xlabel("Number of Points (N)")
    plt.ylabel("Execution Time (ms)")

    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.show()

def main():

    try:
        n = int(input("Enter number of points: "))

    except ValueError:
        print("Error: N must be an integer.")
        return

    if n < 2:
        print("Error: At least 2 points are required.")
        return

    points = [
        (
            random.randint(-100, 100),
            random.randint(-100, 100)
        )
        for _ in range(n)
    ]

    print("\nGenerated Points:")
    print(points)

    start = time.perf_counter()

    bf_p1, bf_p2, bf_distance = (
        brute_force_closest_pair(points)
    )

    brute_time = (
        time.perf_counter() - start
    ) * 1000

    start = time.perf_counter()

    dc_p1, dc_p2, dc_distance = (
        divide_and_conquer_closest_pair(points)
    )

    divide_time = (
        time.perf_counter() - start
    ) * 1000

    print("\n========== RESULTS ==========")

    print(
        f"\nBrute-Force: "
        f"{bf_distance:.6f}, "
        f"{bf_p1}, {bf_p2}"
    )

    print(
        f"Divide-and-Conquer: "
        f"{dc_distance:.6f}, "
        f"{dc_p1}, {dc_p2}"
    )

    print(
        f"Execution Time: "
        f"Brute Force = {brute_time:.6f} ms, "
        f"Divide & Conquer = {divide_time:.6f} ms"
    )

   
    print("\n--- Verification ---")

    if math.isclose(
        bf_distance,
        dc_distance,
        rel_tol=1e-9,
        abs_tol=1e-12
    ):
        print(
            "PASS: Both algorithms found "
            "the same minimum distance."
        )
    else:
        print(
            "FAIL: Algorithms returned "
            "different minimum distances."
        )

    run_corner_case_tests()

    visualize_closest_pair(
        points,
        bf_p1,
        bf_p2,
        dc_p1,
        dc_p2,
        dc_distance
    )

    performance_analysis()
if __name__ == "__main__":
    main()