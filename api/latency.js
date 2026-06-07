export default function handler(req, res) {
  const start = Date.now();
  // Simulate minimal processing
  const latency = Date.now() - start;
  res.status(200).json({
    latency,
    timestamp: new Date().toISOString(),
    region: process.env.VERCEL_REGION || "unknown"
  });
}
