"use client";

import DailySchedule from "./DailySchedule";
import ImpactReport from "./ImpactReport";
import StatusPanel from "./StatusPanel";

export default function Dashboard() {
    return (
        <div className="grid gap-6 p-4 md:grid-cols-2 lg:grid-cols-3">
            <StatusPanel />
            <DailySchedule />
            <ImpactReport />
            {/* Add more widgets as needed */}
        </div>
    );
}
