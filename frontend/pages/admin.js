import { useEffect, useState } from "react";
import axios from "axios";
import { DataGrid } from "@mui/x-data-grid";

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/get_users").then((response) => {
      setUsers(response.data);
    });
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-2xl">Admin Dashboard</h2>
      <DataGrid
        rows={users}
        columns={[
          { field: "id", headerName: "ID", width: 90 },
          { field: "email", headerName: "Email", width: 200 },
          { field: "credits", headerName: "Credits", width: 120 },
        ]}
        pageSize={5}
      />
    </div>
  );
}
