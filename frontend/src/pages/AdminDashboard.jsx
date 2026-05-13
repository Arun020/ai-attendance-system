import { useEffect, useState } from "react";
import API from "../api/api";
import StatCard from "../components/StatCard";

function AdminDashboard() {

  const [data, setData] = useState({
    total: 0,
    present: 0,
    absent: 0
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const res = await API.get("/attendance-summary");

      setData(res.data);

    } catch (err) {
      console.log(err);
    }
  };

  return (
    <div>

      <h1 style={{ marginBottom: "20px" }}>AI Attendance Dashboard</h1>

      {/* KPI ROW */}
      <div style={{
        display: "flex",
        gap: "20px",
        marginBottom: "30px"
      }}>

        <StatCard title="Total Students" value={data.total} />
        <StatCard title="Present %" value={`${data.present}%`} />
        <StatCard title="Absent %" value={`${data.absent}%`} />

      </div>

      {/* TABLE / EMPTY STATE */}
      <div style={{
        background: "white",
        padding: "20px",
        borderRadius: "12px",
        boxShadow: "0 10px 20px rgba(0,0,0,0.05)"
      }}>

        <h3>Defaulters</h3>

        <p style={{ color: "#6b7280" }}>
          No defaulters found
        </p>

      </div>

    </div>
  );
}

export default AdminDashboard;