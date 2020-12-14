export interface DashboardAPI {
    id: number;
    name: string;
    description: string;
    is_default_dashboard: boolean;
}

export class Dashboard {
    constructor(public id: number, public name: string, public description: string, public isDefault: boolean) {
    }
}

export interface DefaultDashboardAPI {
    default_dashboard_id: number;
    default_dashboard_url: string;
}

export class DefaultDashboard {
    constructor(public defaultDashboardID: number, public defaultDashboardURL: string) {}

}
