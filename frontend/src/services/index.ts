import { auditService } from "./audit.service";
import { authService } from "./auth.service";
import { dashboardService } from "./dashboard.service";
import { dictamenesService } from "./dictamenes.service";
import { evidenceService } from "./evidence.service";
import { notificationsService } from "./notifications.service";
import { plansService } from "./plans.service";
import { recommendationsService } from "./recommendations.service";
import { reportsService } from "./reports.service";
import { unitsService } from "./units.service";
import { usersService } from "./users.service";

export const api = {
  login: authService.login,
  listRecommendations: recommendationsService.list,
  listRecommendationsPage: recommendationsService.listPage,
  getRecommendation: recommendationsService.get,
  createRecommendation: recommendationsService.create,
  updateRecommendation: recommendationsService.update,
  listPlan: plansService.list,
  createPlan: plansService.create,
  uploadEvidence: evidenceService.upload,
  getEvidenceFile: evidenceService.getFile,
  cancelEvidence: evidenceService.cancel,
  verifyEvidenceIntegrity: evidenceService.verifyIntegrity,
  submitDictamen: dictamenesService.create,
  getDictamen: dictamenesService.get,
  listReports: reportsService.list,
  listReportsPage: reportsService.listPage,
  createReport: reportsService.create,
  getReport: reportsService.get,
  downloadReportDocument: reportsService.downloadDocument,
  listUnits: unitsService.list,
  createUnit: unitsService.create,
  listUsers: usersService.list,
  updateUser: usersService.update,
  getDashboard: dashboardService.get,
  getDashboardKPIs: dashboardService.getKPIs,
  getHealth: dashboardService.getHealth,
  getAuditLog: auditService.list,
  downloadMatriz: auditService.downloadMatrix,
  listNotifications: notificationsService.list,
  getPreferences: notificationsService.getPreferences,
  updatePreferences: notificationsService.updatePreferences,
  getNotificationSettings: notificationsService.getSettings,
  updateNotificationSettings: notificationsService.updateSettings,
};

export * from "./apiClient";
export * from "./audit.service";
export * from "./auth.service";
export * from "./dashboard.service";
export * from "./dictamenes.service";
export * from "./evidence.service";
export * from "./notifications.service";
export * from "./plans.service";
export * from "./recommendations.service";
export * from "./reports.service";
export * from "./units.service";
export * from "./users.service";
