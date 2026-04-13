import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MaterialModule } from '../../../../../Shared/Modules/MaterialModule';
import { Navbar } from '../../../Navbar/Pages/navbar/navbar';


export interface ReasonCard {
  groupLabel: string;    // e.g. "Role Redundancy"
  count: number;         // total employees in this group
  color: string;
  reasons: {             // individual raw reasons inside this group
    label: string;       // e.g. "Role redundancy"
    count: number;
    feedbacks: string[]; // from feedback_by_reason
  }[];
}
@Component({
  selector: 'app-exit-reason',
  imports: [CommonModule, MaterialModule, Navbar],
  templateUrl: './exit-reason.html',
  styleUrl: './exit-reason.scss',
})


export class ExitReasons implements OnInit {

  pageTitle  = '';
  startDate  = '';
  endDate    = '';
  reasonCards: ReasonCard[] = [];

  // Maps each raw API reason key → display group name
  private readonly REASON_GROUPS: { [key: string]: string } = {
    'role redundancy':                 'Role Redundancy',
    'lack of growth opportunities':    'Career Growth',
    'career change':                   'Career Growth',
    'dissatisfaction with management': 'Management & Leadership',
    'toxic work environment':          'Management & Leadership',
    'seeking higher salary':           'Business Challenges',
    'better work-life balance':        'Business Challenges',
    'personal reasons':                'Business Challenges'
  };

  private readonly GROUP_COLORS: { [key: string]: string } = {
    'Role Redundancy':         '#6366F1',
    'Career Growth':           '#8B5CF6',
    'Management & Leadership': '#EC4899',
    'Business Challenges':     '#F59E0B'
  };

  // Fixed display order
  private readonly GROUP_ORDER = [
    'Role Redundancy', 'Career Growth', 'Management & Leadership', 'Business Challenges'
  ];

  constructor(private router: Router) {}

  ngOnInit(): void {
    const state = history.state as {
      title?:             string;
      startDate?:         string;
      endDate?:           string;
      reasonCounts?:      { [key: string]: number };
      feedbackByReason?:  { [key: string]: string[] };
      overallPercentage?: { [key: string]: string };
    };

    this.pageTitle  = state?.title    ?? 'Exit Analysis';
    this.startDate  = state?.startDate ?? '';
    this.endDate    = state?.endDate   ?? '';

    const reasonCounts     = state?.reasonCounts     ?? {};
    const feedbackByReason = state?.feedbackByReason ?? {};

    // Build one card per group, aggregating matching raw reasons
    const groupMap: { [group: string]: ReasonCard } = {};

    this.GROUP_ORDER.forEach(group => {
      groupMap[group] = {
        groupLabel: group,
        count: 0,
        color: this.GROUP_COLORS[group],
        reasons: []
      };
    });

    // Iterate every raw reason from the API
    Object.entries(reasonCounts).forEach(([rawReason, count]) => {
      const group = this.REASON_GROUPS[rawReason];
      if (!group || !groupMap[group]) return;

      groupMap[group].count += count;
      groupMap[group].reasons.push({
        label:     rawReason.charAt(0).toUpperCase() + rawReason.slice(1),
        count,
        feedbacks: feedbackByReason[rawReason] ?? []
      });
    });

    // Only include groups that have at least one employee
    this.reasonCards = this.GROUP_ORDER
      .map(g => groupMap[g])
      .filter(card => card.count > 0);
  }

  goBack(): void {
    this.router.navigate(['/report']);
  }
}





































