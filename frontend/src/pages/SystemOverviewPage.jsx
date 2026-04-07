import { useOutletContext } from "react-router-dom";
import DataRateLatencyChart from "../charts/DataRateLatencyChart";
import DriftScoreLineChart from "../charts/DriftScoreLineChart";
import ConfidenceHistogramChart from "../charts/ConfidenceHistogramChart";
import MetricCard from "../components/MetricCard";
import SectionCard from "../components/SectionCard";

export default function SystemOverviewPage() {
  const { dashboardData } = useOutletContext();
  const latest = dashboardData.overview.series.at(-1);

  return (
    <div className="page-stack">
      <div className="dashboard-grid dashboard-grid-3">
        <MetricCard label="System Status" value={dashboardData.overview.systemStatus} hint="Composite health signal" status={dashboardData.overview.systemStatus} />
        <MetricCard label="Data Rate" value={`${latest.dataRate} eps`} hint="Current stream ingress" />
        <MetricCard label="Drift Score" value={latest.driftScore} hint="Combined drift detector score" />
        <MetricCard label="Active Model Version" value={dashboardData.overview.activeModelVersion} hint="Serving model in production" />
        <MetricCard label="Latency" value={`${latest.latency} ms`} hint="End-to-end processing latency" />
        <MetricCard label="Kafka Lag" value={`${latest.kafkaLag}`} hint="Unprocessed backlog count" />
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Data Rate vs Latency"
          subtitle="Real-time throughput and responsiveness"
        >
          <DataRateLatencyChart data={dashboardData.overview.series} />
        </SectionCard>

        <SectionCard
          title="Drift Score Over Time"
          subtitle="Watch early drift escalation"
        >
          <DriftScoreLineChart data={dashboardData.overview.series} />
        </SectionCard>
      </div>

      <SectionCard
        title="Confidence Distribution"
        subtitle="Prediction confidence histogram"
      >
        <ConfidenceHistogramChart data={dashboardData.overview.confidenceHistogram} />
      </SectionCard>
    </div>
  );
}
