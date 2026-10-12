export type WaterLevelStatus = 'Critical' | 'Low' | 'Normal' | 'High' | 'Offline' | 'Unavailable' | 'Unknown';
export type DeviceConnectionStatus = 'Online' | 'Offline' | 'Unknown';

export interface WaterLevelData {
  percentage: number | null;
  water_level_cm: number | null;
  status: WaterLevelStatus;
  device_status?: DeviceConnectionStatus;
  source: string;
  timestamp: string | null;
  alert_triggered?: boolean;
  alert_sent?: boolean;
  error?: string;
  detail?: string;
  configured?: boolean;
}
