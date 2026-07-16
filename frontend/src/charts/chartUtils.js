export const chartAnimation = {
  isAnimationActive: true,
  animationDuration: 420,
  animationEasing: "ease-out",
};

export function getSampleDomain(data) {
  if (!data?.length) {
    return [0, 1];
  }
  const first = data[0]?.sampleIndex ?? 0;
  const last = data[data.length - 1]?.sampleIndex ?? first + 1;
  return [first, Math.max(first + 1, last)];
}

export function makeTimeFormatter(data) {
  const lookup = new Map((data ?? []).map((point) => [point.sampleIndex, point.time]));
  return (value) => lookup.get(value) ?? "";
}

export function getLastPoint(data) {
  return data?.length ? data[data.length - 1] : null;
}
