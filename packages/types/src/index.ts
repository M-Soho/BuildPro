// Core domain types
export * from "./domain/tenant";
export * from "./domain/user";
export * from "./domain/project";
export * from "./domain/material";
export * from "./domain/schedule";
export * from "./domain/report";

// API types
export * from "./api/responses";
export * from "./api/pagination";

// Common types
export type UUID = string;
export type Timestamp = string; // ISO 8601
export type TenantId = UUID;
export type UserId = UUID;
export type ProjectId = UUID;
