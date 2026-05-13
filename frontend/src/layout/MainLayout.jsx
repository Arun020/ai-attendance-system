import Sidebar from "../components/Sidebar";

function MainLayout({ children }) {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "#f6f7fb" }}>

      <Sidebar />

      <div style={{ flex: 1, padding: "20px" }}>
        {children}
      </div>

    </div>
  );
}

export default MainLayout;