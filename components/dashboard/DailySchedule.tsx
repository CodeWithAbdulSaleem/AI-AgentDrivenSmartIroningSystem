export default function DailySchedule() {
    return (
        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Daily Schedule</h3>
            <div className="mt-4">
                {/* Placeholder for schedule items */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between border-b border-gray-100 pb-2 dark:border-gray-700">
                        <span className="text-sm text-gray-600 dark:text-gray-300">09:00 AM</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">Start Ironing</span>
                    </div>
                    <div className="flex items-center justify-between border-b border-gray-100 pb-2 dark:border-gray-700">
                        <span className="text-sm text-gray-600 dark:text-gray-300">05:00 PM</span>
                        <span className="text-sm font-medium text-gray-900 dark:text-white">End Session</span>
                    </div>
                </div>
            </div>
        </div>
    );
}
