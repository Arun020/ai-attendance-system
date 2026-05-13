function Sidebar() {
  return (
    <div style={{
      width: "240px",
      background: "#111827",
      color: "white",
      padding: "20px",
      display: "flex",
      flexDirection: "column",
      gap: "20px"
    }}>

      <h2 style={{ color: "#fff" }}>AI Attendance</h2>

      <div>📊 Dashboard</div>
      <div>👨‍🎓 Students</div>
      <div>📅 Attendance</div>
      <div>⚠️ Defaulters</div>
      <div>⚙️ Settings</div>

    </div>
  );
}

export default Sidebar;