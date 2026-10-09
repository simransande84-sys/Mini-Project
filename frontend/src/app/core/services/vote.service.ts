import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';
import { VoteResponse } from '../models/complaint.model';

@Injectable({ providedIn: 'root' })
export class VoteService {
  constructor(private http: HttpClient) {}

  private url(id: number) {
    return `${environment.apiUrl}/complaints/${id}/vote/`;
  }

  getStatus(id: number): Observable<{ user_has_voted: boolean; support_count: number }> {
    return this.http.get<{ user_has_voted: boolean; support_count: number }>(this.url(id));
  }

  castVote(id: number): Observable<VoteResponse> {
    return this.http.post<VoteResponse>(this.url(id), {});
  }

  removeVote(id: number): Observable<VoteResponse> {
    return this.http.delete<VoteResponse>(this.url(id));
  }
}
