import java.io.*;
import java.util.*;

public class main {

    static class Flight {
        int to, price, id;

        Flight(int to, int price, int id) {
            this.to = to;
            this.price = price;
            this.id = id;
        }
    }

    static class State implements Comparable<State> {
        int city, flights, coupons;
        long cost;

        State(int city, int flights, int coupons, long cost) {
            this.city = city;
            this.flights = flights;
            this.coupons = coupons;
            this.cost = cost;
        }

        public int compareTo(State s) {
            return Long.compare(cost, s.cost);
        }
    }

    static class Parent {
        int city, flights, coupons, edge;
        boolean discounted;

        Parent(int city, int flights, int coupons,
               int edge, boolean discounted) {
            this.city = city;
            this.flights = flights;
            this.coupons = coupons;
            this.edge = edge;
            this.discounted = discounted;
        }
    }

    static int N, M, K, C, limit;
    static int[] from, to, price;
    static List<Flight>[] graph;
    static long[][][] dist;
    static Parent[][][] parent;

    public static void main(String[] args) throws Exception {

        Scanner sc = new Scanner(System.in);
        N = sc.nextInt();
        M = sc.nextInt();
        K = sc.nextInt();
        C = sc.nextInt();

        if (N < 1 || M < 0 || K < 0 || C < 0) {
            System.out.println("Invalid input");
            sc.close();
            return;
        }

        from = new int[M];
        to = new int[M];
        price = new int[M];

        graph = new ArrayList[N + 1];

        for (int i = 0; i <= N; i++) {
            graph[i] = new ArrayList<>();
        }

        for (int i = 0; i < M; i++) {
            from[i] = sc.nextInt();
            to[i] = sc.nextInt();
            price[i] = sc.nextInt();

            if (from[i] < 1 || from[i] > N ||
                to[i] < 1 || to[i] > N ||
                price[i] < 0) {
                System.out.println("Invalid flight");
                sc.close();
                return;
            }

            graph[from[i]].add(
                new Flight(to[i], price[i], i)
            );
        }

        sc.close();
        limit = (int) Math.min((long) K + 1, (long) N - 1);

        dist = new long[N + 1][limit + 1][C + 1];
        parent = new Parent[N + 1][limit + 1][C + 1];

        for (int i = 1; i <= N; i++) {
            for (int f = 0; f <= limit; f++) {
                Arrays.fill(dist[i][f], Long.MAX_VALUE);
            }
        }

        PriorityQueue<State> pq = new PriorityQueue<>();

        dist[1][0][0] = 0;
        pq.offer(new State(1, 0, 0, 0));

        while (!pq.isEmpty()) {
            State cur = pq.poll();

            if (cur.cost !=
                dist[cur.city][cur.flights][cur.coupons]) {
                continue;
            }

            if (cur.flights == limit) {
                continue;
            }

            for (Flight e : graph[cur.city]) {
                int nf = cur.flights + 1;
                long normal = cur.cost + e.price;

                if (normal < dist[e.to][nf][cur.coupons]) {
                    dist[e.to][nf][cur.coupons] = normal;

                    parent[e.to][nf][cur.coupons] =
                        new Parent(cur.city, cur.flights,
                                   cur.coupons, e.id, false);

                    pq.offer(new State(e.to, nf,
                                       cur.coupons, normal));
                }
                if (cur.coupons < C) {
                    int nc = cur.coupons + 1;
                    long discounted = cur.cost + e.price / 2;

                    if (discounted < dist[e.to][nf][nc]) {
                        dist[e.to][nf][nc] = discounted;

                        parent[e.to][nf][nc] =
                            new Parent(cur.city, cur.flights,
                                       cur.coupons, e.id, true);

                        pq.offer(new State(e.to, nf,
                                           nc, discounted));
                    }
                }
            }
        }
        long best = Long.MAX_VALUE;
        int bestF = -1, bestC = -1;

        for (int f = 0; f <= limit; f++) {
            for (int c = 0; c <= C; c++) {
                if (dist[N][f][c] < best) {
                    best = dist[N][f][c];
                    bestF = f;
                    bestC = c;
                }
            }
        }

        if (best == Long.MAX_VALUE) {
            System.out.println(-1);
            return;
        }

        System.out.println("Minimum cost: " + best);
        System.out.println("Flights taken: " + bestF);
        System.out.println("Intermediate stops: " +
                           Math.max(0, bestF - 1));
        System.out.println("Coupons used: " + bestC);
        boolean[] chosen = new boolean[M];
        boolean[] usedCoupon = new boolean[M];
        List<Integer> routeEdges = new ArrayList<>();

        int city = N;
        int f = bestF;
        int c = bestC;

        while (f > 0) {
            Parent p = parent[city][f][c];

            if (p == null) {
                throw new IllegalStateException(
                    "Route reconstruction failed"
                );
            }

            routeEdges.add(p.edge);
            chosen[p.edge] = true;
            usedCoupon[p.edge] = p.discounted;

            city = p.city;
            f = p.flights;
            c = p.coupons;
        }

        Collections.reverse(routeEdges);

        System.out.print("Route: 1");

        for (int edgeId : routeEdges) {
            System.out.print(" -> " + to[edgeId]);
        }

        System.out.println();
        try (PrintWriter out =
                 new PrintWriter("flight_path.csv")) {

            out.println(
                "From,To,OriginalPrice,Selected,CouponUsed,FinalPrice"
            );

            for (int i = 0; i < M; i++) {
                String mark = chosen[i] ? "x" : "";
                String coupon = usedCoupon[i] ? "Yes" : "No";
                String finalPrice = "";

                if (chosen[i]) {
                    finalPrice = String.valueOf(
                        usedCoupon[i] ? price[i] / 2 : price[i]
                    );
                }

                out.printf("%d,%d,%d,%s,%s,%s%n",
                    from[i], to[i], price[i],
                    mark, coupon, finalPrice);
            }
        }

        System.out.println("CSV created: flight_path.csv");
    }
}