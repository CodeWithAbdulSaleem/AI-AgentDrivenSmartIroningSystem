import Dashboard from "@/components/dashboard/Dashboard";

export default function Home() {
    return (
        <main className="flex min-h-screen flex-col p-6">
            <div className="mb-8 flex items-center justify-between">
                <h1 className="text-3xl font-bold">Smart Ironing System</h1>
                <div className="text-sm text-gray-500">Dashboard</div>
            </div>
            <Dashboard />
        </main>
    );
}
