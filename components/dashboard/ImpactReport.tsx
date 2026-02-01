export default function ImpactReport() {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Impact Report</h3>
            <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="rounded-lg bg-blue-50 p-3 dark:bg-blue-900/20">
                    <p className="text-sm text-blue-600 dark:text-blue-400">Energy Saved</p>
                    <p className="mt-1 text-2xl font-bold text-blue-700 dark:text-blue-300">12%</p>
                </div>
                <div className="rounded-lg bg-green-50 p-3 dark:bg-green-900/20">
                    <p className="text-sm text-green-600 dark:text-green-400">Efficiency</p>
                    <p className="mt-1 text-2xl font-bold text-green-700 dark:text-green-300">High</p>
                </div>
            </div>
        </div>
    );
}
