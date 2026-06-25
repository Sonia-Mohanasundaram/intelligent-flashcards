import { createFileRoute } from "@tanstack/react-router";
import { AppLayout } from "@/components/AppLayout";
import { useStore } from "@/lib/store";
import { ResponsiveContainer, Tooltip, PieChart, Pie, Cell, Legend } from "recharts";

export const Route = createFileRoute("/statistics")({
  head: () => ({ meta: [{ title: "intelligent-flashcards" }] }),
  component: () => <AppLayout><Page /></AppLayout>,
});

function Page() {
  const { state } = useStore();

  const total = state.cards.length;
  const known = state.cards.filter((c) => c.known).length;
  const saved = state.cards.filter((c) => c.saved).length;
  const favorite = state.cards.filter((c) => c.favorite).length;
  const completion = total ? Math.round((known / total) * 100) : 0;

  const diffCounts = state.cards.reduce<Record<string, number>>((acc, c) => {
    acc[c.difficulty] = (acc[c.difficulty] ?? 0) + 1; return acc;
  }, { Easy: 0, Medium: 0, Hard: 0 });
  const pieData = Object.entries(diffCounts).map(([name, value]) => ({ name, value }));
  const pieColors = ["oklch(0.65 0.17 150)", "oklch(0.75 0.16 60)", "oklch(0.6 0.23 25)"];

  return (
    <div className="px-4 md:px-8 py-6 md:py-10 max-w-6xl mx-auto space-y-6">
      <header>
        <h1 className="font-display font-bold text-3xl">📊 Statistics</h1>
        <p className="text-sm text-muted-foreground">Track your learning progress and flashcard performance.</p>
      </header>

      <section className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Stat label="Total Notes" value={state.sets.length} />
        <Stat label="Total Flashcards" value={total} />
        <Stat label="Known" value={known} />
        <Stat label="In Revision" value={saved} />
        <Stat label="Favorites" value={favorite} />
        <Stat label="Completion" value={`${completion}%`} />
      </section>

      <section className="grid lg:grid-cols-2 gap-4">
        <div className="rounded-3xl bg-card border border-border p-6 shadow-soft">
          <h3 className="font-display font-bold text-lg mb-4">Difficulty Distribution</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={pieData} dataKey="value" innerRadius={50} outerRadius={90} paddingAngle={3}>
                  {pieData.map((_, i) => <Cell key={i} fill={pieColors[i]} />)}
                </Pie>
                <Legend />
                <Tooltip contentStyle={{ background: "var(--card)", border: "1px solid var(--border)", borderRadius: 12 }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>

    </div>
  );
}

function Stat({ label, value, accent }: { label: string; value: number | string; accent?: boolean }) {
  return (
    <div className={`rounded-2xl p-5 border ${accent ? "bg-gradient-primary text-white border-transparent shadow-elegant" : "bg-card border-border shadow-soft"}`}>
      <div className={`text-xs ${accent ? "text-white/80" : "text-muted-foreground"}`}>{label}</div>
      <div className="text-2xl font-display font-bold mt-1">{value}</div>
    </div>
  );
}
