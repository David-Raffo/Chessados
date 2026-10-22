import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Chess } from "chess.js";
import { isPromotion, toDests, uciToKeys, type Color, type Key } from "../components/Board";
import { sound } from "./sound";
import type { Puzzle } from "./types";

export type PuzzleStatus = "intro" | "play" | "solved" | "failed";

/**
 * Motor de un puzzle de Lichess: la primera jugada es del rival, después se alternan
 * la jugada esperada del usuario y la respuesta automática.
 */
export function usePuzzle(puzzle: Puzzle | null, opts: { onDone?: (solved: boolean, seconds: number) => void } = {}) {
  const chess = useRef(new Chess());
  const [fen, setFen] = useState(chess.current.fen());
  const [lastMove, setLastMove] = useState<Key[] | undefined>();
  const [idx, setIdx] = useState(0);
  const [status, setStatus] = useState<PuzzleStatus>("intro");
  const [mistake, setMistake] = useState(false); // ya ha fallado una vez (el puzzle cuenta como fallado)
  const [recovered, setRecovered] = useState(false); // lo terminó bien tras fallar o reintentar
  const [flash, setFlash] = useState<"good" | "bad" | null>(null);
  const [promo, setPromo] = useState<{ from: Key; to: Key } | null>(null);
  const startedAt = useRef(0);
  const reported = useRef(false);
  const onDone = useRef(opts.onDone);
  onDone.current = opts.onDone;

  const color: Color = useMemo(() => {
    if (!puzzle) return "white";
    return puzzle.fen.split(" ")[1] === "w" ? "black" : "white"; // juegas el bando contrario al que mueve primero
  }, [puzzle]);

  const apply = useCallback((uci: string) => {
    const [from, to] = uciToKeys(uci);
    const move = chess.current.move({ from, to, promotion: uci[4] });
    setLastMove([from, to]);
    setFen(chess.current.fen());
    if (chess.current.inCheck()) sound.check();
    else if (move.captured) sound.capture();
    else sound.move();
  }, []);

  const report = useCallback((solved: boolean) => {
    if (reported.current) return;
    reported.current = true;
    onDone.current?.(solved, (performance.now() - startedAt.current) / 1000);
  }, []);

  useEffect(() => {
    if (!puzzle) return;
    chess.current = new Chess(puzzle.fen);
    setFen(puzzle.fen);
    setLastMove(undefined);
    setIdx(0);
    setStatus("intro");
    setMistake(false);
    setRecovered(false);
    setFlash(null);
    reported.current = false;
    const t = window.setTimeout(() => {
      apply(puzzle.moves[0]);
      setIdx(1);
      setStatus("play");
      startedAt.current = performance.now();
    }, 500);
    return () => window.clearTimeout(t);
  }, [puzzle, apply]);

  const fail = useCallback(() => {
    setMistake(true);
    setFlash("bad");
    sound.bad();
    report(false);
    window.setTimeout(() => setFlash(null), 400);
  }, [report]);

  const userMove = useCallback(
    (from: Key, to: Key, promotion?: string) => {
      if (!puzzle || status !== "play") return;
      if (!promotion && isPromotion(chess.current, from, to)) {
        setPromo({ from, to });
        return;
      }
      const expected = puzzle.moves[idx];
      const uci = `${from}${to}${promotion ?? ""}`;
      let move;
      try {
        move = chess.current.move({ from, to, promotion });
      } catch {
        setFen(chess.current.fen());
        return;
      }
      // Cualquier jugada que dé mate también es correcta
      const ok = uci === expected || chess.current.isCheckmate();
      if (!ok) {
        chess.current.undo();
        setFen(chess.current.fen());
        fail();
        return;
      }
      setLastMove([from, to]);
      setFen(chess.current.fen());
      if (move.captured) sound.capture();
      else sound.move();
      const next = idx + 1;
      if (next >= puzzle.moves.length || chess.current.isCheckmate()) {
        setIdx(puzzle.moves.length);
        setStatus(mistake ? "failed" : "solved");
        setRecovered(mistake);
        setFlash("good");
        sound.good();
        report(!mistake);
        return;
      }
      setIdx(next + 1);
      window.setTimeout(() => {
        apply(puzzle.moves[next]);
        if (next + 1 >= puzzle.moves.length) {
          setStatus(mistake ? "failed" : "solved");
          report(!mistake);
        }
      }, 300);
    },
    [apply, fail, idx, mistake, puzzle, report, status],
  );

  /** Muestra la solución jugada a jugada (cuenta como fallo). */
  const showSolution = useCallback(() => {
    if (!puzzle || status !== "play") return;
    setMistake(true);
    report(false);
    setStatus("failed");
    const remaining = puzzle.moves.slice(idx);
    remaining.forEach((uci, i) => window.setTimeout(() => apply(uci), 450 * (i + 1)));
    setIdx(puzzle.moves.length);
  }, [apply, idx, puzzle, report, status]);

  /** Vuelve a la posición inicial del puzzle para intentarlo de nuevo (ya cuenta como fallado). */
  const retry = useCallback(() => {
    if (!puzzle) return;
    chess.current = new Chess(puzzle.fen);
    apply(puzzle.moves[0]);
    setIdx(1);
    setMistake(true);
    setRecovered(false);
    setFlash(null);
    setStatus("play");
  }, [apply, puzzle]);

  const hint = useMemo((): Key | null => {
    if (!puzzle || status !== "play" || idx >= puzzle.moves.length) return null;
    return puzzle.moves[idx].slice(0, 2) as Key;
  }, [idx, puzzle, status]);

  const dests = useMemo(() => toDests(chess.current), [fen]);

  return {
    fen,
    lastMove,
    color,
    status,
    mistake,
    recovered,
    flash,
    promo,
    setPromo,
    dests,
    hint,
    check: chess.current.inCheck(),
    userMove,
    fail,
    showSolution,
    retry,
    turn: (chess.current.turn() === "w" ? "white" : "black") as Color,
    resetPromo: () => {
      setPromo(null);
      setFen(chess.current.fen());
    },
  };
}
