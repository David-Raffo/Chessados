export type Area = "tactics" | "play" | "endgames" | "openings";
export type RatingArea = "play" | "tactics" | "endgames" | "rush";

export interface User {
  id: number;
  name: string;
  username: string;
  is_admin: boolean;
  weekly_hours: number;
  target_split: Record<Area, number>;
  ladder_elo: number;
  review_lock: boolean;
  lichess_username: string | null;
  chesscom_username: string | null;
  endgame_boost_until: string | null;
}

export interface Puzzle {
  id: string;
  fen: string;
  moves: string[];
  rating: number;
  themes: string[];
  opening: string | null;
  review?: boolean;
}

export interface MoveAnalysis {
  ply: number;
  san: string;
  uci: string;
  fen_before: string;
  eval_cp: number;
  mate: number | null;
  best_uci: string | null;
  best_san: string | null;
  pv_san: string | null;
  classification: "best" | "good" | "inaccuracy" | "mistake" | "blunder";
  phase: "opening" | "middlegame" | "endgame";
  error_type: string | null;
  is_user_move: boolean;
}

export interface Game {
  id: number;
  pgn: string;
  source: string;
  opponent: string;
  opponent_elo: number | null;
  time_control: string | null;
  user_color: "white" | "black";
  result: string;
  user_result: "win" | "loss" | "draw" | null;
  reviewed: boolean;
  user_notes: string | null;
  /** pending → running → quick (análisis rápido listo) → refining (afinando) → done */
  analysis_status: "pending" | "running" | "quick" | "refining" | "done" | "error";
  analysis_depth?: number | null;
  accuracy: number | null;
  played_at: string | null;
  analysis?: MoveAnalysis[];
}

export interface PlanStep {
  area: Area;
  kind: "puzzles" | "game" | "review" | "rush" | "endgame" | "openings" | "woodpecker" | "daily" | "lesson";
  minutes: number;
  title: string;
  theme?: string | null;
  game_id?: number;
  lesson_id?: string;
  progress?: number;
  done?: boolean;
  status?: string;
  seconds?: number;
  target_seconds?: number;
  /** Solo en sugerencias extra */
  reason?: string;
  review?: boolean;
}

export interface Advice {
  rule: number;
  area: string;
  text: string;
  theme?: string;
  game_id?: number;
  link?: string | null;
}

export interface CoachPlan {
  minutes: number;
  split: Record<Area, number>;
  steps: PlanStep[];
  advice: Advice[];
  weak_themes: { theme: string; attempts: number; accuracy: number; avg_seconds: number }[];
  /** Actividades extra para cuando la sesión está completa */
  extras?: PlanStep[];
}
