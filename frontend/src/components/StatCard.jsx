function StatCard({ title, value }) {
  return (
    <div style={{
      background: "white",
      padding: "20px",
      borderRadius: "12px",
      boxShadow: "0 10px 20px rgba(0,0,0,0.05)",
      flex: 1
    }}>

      <h4 style={{ color: "#6b7280" }}>{title}</h4>
      <h2 style={{ marginTop: "10px" }}>{value}</h2>

    </div>
  );
}

export default StatCard;