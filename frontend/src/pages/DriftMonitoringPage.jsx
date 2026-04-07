import { useOutletContext } from "react-router-dom";
import AccuracyErrorChart from "../charts/AccuracyErrorChart";
import ConfidenceTrendChart from "../charts/ConfidenceTrendChart";
import DistributionShiftChart from "../charts/DistributionShiftChart";
import FeatureDriftBarChart from "../charts/FeatureDriftBarChart";
import AlertsTimeline from "../components/AlertsTimeline";
import SectionCard from "../components/SectionCard";

export default function DriftMonitoringPage() {
  const { dashboardData } = useOutletContext();

  return (
    <div className="page-stack">
      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Feature Distribution Shift"
          subtitle="Baseline vs current distribution snapshots"
        >
          <DistributionShiftChart data={dashboardData.drift.featureDistributionShift} />
        </SectionCard>

        <SectionCard
          title="Drift Score Per Feature"
          subtitle="Feature-level drift intensity"
        >
          <FeatureDriftBarChart data={dashboardData.drift.featureScores} />
        </SectionCard>
      </div>

      <div className="dashboard-grid dashboard-grid-2">
        <SectionCard
          title="Concept Drift"
          subtitle="Accuracy and error trend over time"
        >
          <AccuracyErrorChart data={dashboardData.drift.conceptSeries} />
        </SectionCard>

        <SectionCard
          title="Confidence Trend"
          subtitle="Confidence stability in streaming predictions"
        >
          <ConfidenceTrendChart data={dashboardData.drift.conceptSeries} />
        </SectionCard>
      </div>

      <SectionCard
        title="Alerts Timeline"
        subtitle="Latest drift and confidence-related events"
      >
        <AlertsTimeline alerts={dashboardData.drift.alerts} />
      </SectionCard>
    </div>
  );
}
