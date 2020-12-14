export interface Role {
    id?: number;
    name?: string;
    default?: boolean;
    permissions?: number;
    control?: string;
    permission_codes: string[];
}