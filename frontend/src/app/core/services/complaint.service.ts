import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import {
  Complaint, ComplaintCreatePayload, PaginatedResponse,
  PredictPayload, PredictResponse
} from '../models/complaint.model';

@Injectable({ providedIn: 'root' })
export class ComplaintService {
  private base = `${environment.apiUrl}/complaints`;

  constructor(private http: HttpClient) {}

  // ── List / Filters ───────────────────────────────────────────────────

  getAll(params?: Record<string, string>): Observable<PaginatedResponse<Complaint>> {
    let p = new HttpParams();
    if (params) Object.entries(params).forEach(([k, v]) => { if (v) p = p.set(k, v); });
    return this.http.get<PaginatedResponse<Complaint>>(`${this.base}/`, { params: p });
  }

  getMine(): Observable<Complaint[]> {
    return this.http.get<Complaint[]>(`${this.base}/mine/`);
  }

  getPublic(): Observable<Complaint[]> {
    return this.http.get<Complaint[]>(`${this.base}/public/`);
  }

  getById(id: number): Observable<Complaint> {
    return this.http.get<Complaint>(`${this.base}/${id}/`);
  }

  // ── Create / Update / Delete ─────────────────────────────────────────

  create(payload: ComplaintCreatePayload): Observable<Complaint> {
    return this.http.post<Complaint>(`${this.base}/`, payload);
  }

  updateStatus(id: number, status: string): Observable<Complaint> {
    return this.http.patch<Complaint>(`${this.base}/${id}/status/`, { status });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}/`);
  }

  // ── ML Prediction (no DB save) ───────────────────────────────────────

  predict(payload: PredictPayload): Observable<PredictResponse> {
    return this.http.post<PredictResponse>(`${environment.apiUrl}/predict/`, payload);
  }
}
