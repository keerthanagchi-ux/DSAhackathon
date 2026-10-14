import java.io.*;
import java.util.*;

public class Visualize {

    static class Flight {
        int from, to, price, finalPrice;
        boolean selected, coupon;

        Flight(int from, int to, int price,
               boolean selected, boolean coupon, int finalPrice) {
            this.from = from;
            this.to = to;
            this.price = price;
            this.selected = selected;
            this.coupon = coupon;
            this.finalPrice = finalPrice;
        }
    }

    public static void main(String[] args) throws Exception {
        List<Flight> flights = new ArrayList<>();
        Set<Integer> cities = new TreeSet<>();

        try (BufferedReader br =
                 new BufferedReader(new FileReader("flight_path.csv"))) {
            String line;
            br.readLine();

            while ((line = br.readLine()) != null) {
                String[] a = line.split(",", -1);

                flights.add(new Flight(
                    Integer.parseInt(a[0]),
                    Integer.parseInt(a[1]),
                    Integer.parseInt(a[2]),
                    a[3].equalsIgnoreCase("x"),
                    a[4].equalsIgnoreCase("Yes"),
                    a[5].isEmpty()
                        ? Integer.parseInt(a[2])
                        : Integer.parseInt(a[5])
                ));

                cities.add(Integer.parseInt(a[0]));
                cities.add(Integer.parseInt(a[1]));
            }
        }

        if (flights.isEmpty()) {
            System.out.println("CSV contains no flights.");
            return;
        }

        int destination = Collections.max(cities);
        int width = 850, height = 650;
        double cx = width / 2.0, cy = height / 2.0;
        double radius = Math.min(width, height) * 0.36;

        Map<Integer, double[]> pos = new HashMap<>();
        int index = 0;

        for (int city : cities) {
            double angle = -Math.PI / 2
                + 2 * Math.PI * index++ / cities.size();

            pos.put(city, new double[] {
                cx + radius * Math.cos(angle),
                cy + radius * Math.sin(angle)
            });
        }
        List<Flight> route = new ArrayList<>();
        Set<Flight> remaining = new HashSet<>();

        for (Flight f : flights) {
            if (f.selected) remaining.add(f);
        }

        int current = 1;

        while (current != destination) {
            Flight next = null;

            for (Flight f : flights) {
                if (remaining.contains(f) && f.from == current) {
                    next = f;
                    break;
                }
            }

            if (next == null) break;

            route.add(next);
            remaining.remove(next);
            current = next.to;
        }

        try (PrintWriter out =
                 new PrintWriter("flight_graph.html")) {

            out.println("<!DOCTYPE html><html><head>");
            out.println("<meta charset='UTF-8'>");
            out.println("<meta name='viewport' content='width=device-width, initial-scale=1'>");
            out.println("<title>Budget Traveller</title>");

            out.println("<style>");
            out.println("body{font-family:Arial;margin:20px;background:#f1f5f9;color:#172033}");
            out.println("svg{width:100%;max-width:850px;background:white;border:1px solid #ddd;border-radius:12px}");
            out.println(".panel{background:white;padding:14px;border-radius:10px;margin:12px 0;max-width:820px}");
            out.println("button{padding:10px 18px;margin:5px;border:0;border-radius:7px;background:#2563eb;color:white;cursor:pointer}");
            out.println("button:disabled{background:#94a3b8;cursor:default}");
            out.println(".flight{transition:stroke .3s,stroke-width .3s}");
            out.println("</style></head><body>");

            out.println("<h2>Budget Traveller - Flight Network</h2>");
            out.println("<p>🟢 Start &nbsp; 🔴 Destination &nbsp; 🟠 Intermediate city</p>");
            out.println("<p>🔵 Other flight &nbsp; 🔴 Selected route &nbsp; 🟡 Coupon flight</p>");

            out.println("<div class='panel'>");
            out.println("<button id='play' onclick='play()'>▶️ Play Animation</button>");
            out.println("<button onclick='resetJourney()'>↺ Reset</button>");
            out.println("<h3 id='status'>Ready to start the journey</h3>");
            out.println("<p id='step'>Flights completed: 0 / " + route.size() + "</p>");
            out.println("<p id='cost'>Running cost: ₹0</p>");
            out.println("<p id='stops'>Intermediate stops used: 0</p>");
            out.println("<p id='coupon'>Coupon details: None yet</p>");
            out.println("</div>");

            out.printf("<svg viewBox='0 0 %d %d' xmlns='http://www.w3.org/2000/svg'>%n",
                width, height);

            out.println("<defs><marker id='arrow' markerWidth='8' markerHeight='8' refX='7' refY='3' orient='auto'><path d='M0,0 L0,6 L8,3 Z' fill='context-stroke'/></marker></defs>");

            for (int i = 0; i < flights.size(); i++) {
                Flight f = flights.get(i);
                double[] p1 = pos.get(f.from);
                double[] p2 = pos.get(f.to);

                double dx = p2[0] - p1[0];
                double dy = p2[1] - p1[1];
                double len = Math.hypot(dx, dy);

                if (len == 0) {
                    dx = 1;
                    dy = 0;
                    len = 1;
                }

                double x1 = p1[0] + dx / len * 23;
                double y1 = p1[1] + dy / len * 23;
                double x2 = p2[0] - dx / len * 28;
                double y2 = p2[1] - dy / len * 28;

                String color = f.coupon ? "#d4a000"
                    : f.selected ? "#dc2626" : "#64748b";

                out.printf(Locale.US,
                    "<line id='edge%d' class='flight' x1='%.2f' y1='%.2f' x2='%.2f' y2='%.2f' stroke='%s' stroke-width='%d' marker-end='url(#arrow)'/>%n",
                    i, x1, y1, x2, y2, color, f.selected ? 4 : 2);

                String label = f.coupon
                    ? f.price + " -> " + f.finalPrice + " (coupon)"
                    : String.valueOf(f.price);

                out.printf(Locale.US,
                    "<text x='%.2f' y='%.2f' font-size='12' fill='%s'>%s</text>%n",
                    (x1 + x2) / 2, (y1 + y2) / 2 - 5,
                    color, label);
            }

            for (int city : cities) {
                double[] p = pos.get(city);

                String color = city == 1 ? "#16a34a"
                    : city == destination ? "#dc2626" : "#f59e0b";

                out.printf(Locale.US,
                    "<circle id='city%d' cx='%.2f' cy='%.2f' r='22' fill='%s'/>%n",
                    city, p[0], p[1], color);

                out.printf(Locale.US,
                    "<text x='%.2f' y='%.2f' fill='white' font-size='13' text-anchor='middle' dominant-baseline='middle'>%d</text>%n",
                    p[0], p[1], city);
            }

            out.println("</svg>");

        
            out.println("<script>");
            out.println("const route = [");

            for (Flight f : route) {
                int id = flights.indexOf(f);
                out.printf(Locale.US,
                    "{id:%d,from:%d,to:%d,price:%d,finalPrice:%d,coupon:%s},%n",
                    id, f.from, f.to, f.price, f.finalPrice,
                    f.coupon ? "true" : "false");
            }

            out.println("];");
            out.println("let stepIndex=0, runningCost=0, timer=null;");
            out.println("function update(){");
            out.println("document.getElementById('step').textContent='Flights completed: '+stepIndex+' / '+route.length;");
            out.println("document.getElementById('cost').textContent='Running cost: ₹'+runningCost;");
            out.println("document.getElementById('stops').textContent='Intermediate stops used: '+Math.max(0,stepIndex-1);");
            out.println("}");
            out.println("function resetJourney(){");
            out.println("if(timer){clearInterval(timer);timer=null;}");
            out.println("stepIndex=0;runningCost=0;");
            out.println("document.getElementById('status').textContent='Ready to start the journey';");
            out.println("document.getElementById('coupon').textContent='Coupon details: None yet';");
            out.println("document.getElementById('play').disabled=false;");
            out.println("route.forEach(f=>{let e=document.getElementById('edge'+f.id);e.setAttribute('stroke',f.coupon?'#d4a000':'#dc2626');e.setAttribute('stroke-width',4);});");
            out.println("update();");
            out.println("}");
            out.println("function play(){");
            out.println("if(timer)return;");
            out.println("if(stepIndex>=route.length)resetJourney();");
            out.println("document.getElementById('play').disabled=true;");
            out.println("document.getElementById('status').textContent='Journey in progress...';");
            out.println("timer=setInterval(()=>{");
            out.println("if(stepIndex>=route.length){");
            out.println("clearInterval(timer);timer=null;");
            out.println("document.getElementById('status').textContent='Destination reached!';");
            out.println("document.getElementById('play').disabled=false;return;}");
            out.println("const f=route[stepIndex];");
            out.println("const e=document.getElementById('edge'+f.id);");
            out.println("e.setAttribute('stroke',f.coupon?'#d4a000':'#2563eb');");
            out.println("e.setAttribute('stroke-width',7);");
            out.println("runningCost+=f.finalPrice;stepIndex++;");
            out.println("document.getElementById('status').textContent='Flying from city '+f.from+' to city '+f.to;");
            out.println("document.getElementById('coupon').textContent=f.coupon?'Coupon used: ₹'+f.price+' → ₹'+f.finalPrice:'Coupon details: No coupon on this flight';");
            out.println("update();");
            out.println("},1200);");
            out.println("}");
            out.println("update();");
            out.println("</script>");

            out.println("</body></html>");
        }

        System.out.println("Graph created: flight_graph.html");
        System.out.println("Open flight_graph.html in your browser.");
    }
}