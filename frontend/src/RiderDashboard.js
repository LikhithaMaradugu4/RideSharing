import { Link } from "react-router-dom";

function RiderDashboard() {
  return (
    <div>
      <h2>Rider Dashboard</h2>
      <Link to="/app/ride/create">Create Ride</Link>
    </div>
  );
}

export default RiderDashboard;