import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { WaterLevelData } from '../models/water-level.model';

@Injectable({ providedIn: 'root' })
export class WaterLevelService {
  constructor(private http: HttpClient) {}

  /**
   * Retrieves the latest water-level sensor telemetry from the Django backend.
   * Backend handles querying Blynk IoT Cloud datastreams (V0 & V1) and checking alert thresholds.
   */
  getWaterLevel(): Observable<WaterLevelData> {
    return this.http.get<WaterLevelData>(`${environment.apiUrl}/water-level/`);
  }
}
