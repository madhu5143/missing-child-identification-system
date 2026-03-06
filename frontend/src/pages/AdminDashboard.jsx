import Dashboard from './Dashboard';


const AdminDashboard = () => {
    return (
        <div>
            <div className="bg-red-50 p-4 text-red-800 text-center text-sm font-medium mb-6">
                Admin Mode Active: You have full access to manage all cases.
            </div>

            <Dashboard />
        </div>
    );
};

export default AdminDashboard;
