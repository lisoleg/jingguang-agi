-- M133_W1_IdrisSelfRef.idr
-- L4 ICE Y-Combinator Self-Reference Core
-- Part of M133: Self-Referential Loop Topologizer (Week 1)
-- Taiyi-AGI System

module M133_W1_IdrisSelfRef

import Data.Strings
import Data.List

-- ============================================================
-- 1. Core Data Types
-- ============================================================

||| JinlingGraph: adjacency-list graph with port-labeled edges
||| Represents the L3 topological structure of ICE cycles
data JinlingGraph : Type where
    MkGraph : (nodes : List String)
           -> (edges : List (String, String, Int, Int, String))
           -> (version : Int)
           -> JinlingGraph

||| L2Rule: a single L2 inference rule with tag
||| Rules are the logical layer that feeds anomalies upward
data L2Rule : Type where
    MkRule : (name : String)
          -> (premise : List String)
          -> (conclusion : String)
          -> (tag : String)
          -> L2Rule

||| ICEState: the full ICE cycle state
||| Contains L2 rules, L3 graph, and a self-referential fixpoint flag
data ICEState : Type where
    MkICE : (rules : List L2Rule)
         -> (graph : JinlingGraph)
         -> (fixed : Bool)
         -> ICEState

-- ============================================================
-- 2. Self-Ref Y-Combinator (Guarded Recursion)
-- ============================================================

||| Delay: guarded recursion carrier (inspired by Capretta's delay monad)
data Delay : Type -> Type where
    Now   : a -> Delay a
    Later : Lazy (Delay a) -> Delay a

||| Functor instance for Delay
Functor Delay where
    map f (Now x)    = Now (f x)
    map f (Later xs) = Later (map f xs)

||| runDelay: extract value from Delay with fuel counter
runDelay : Int -> Delay a -> Maybe a
runDelay _ (Now x)    = Just x
runDelay 0 (Later _)  = Nothing
runDelay (S k) (Later xs) = runDelay k xs

||| SelfRef: the Y-combinator type for self-referential computation
||| Takes a stepper function and produces a fixed point via guarded recursion
selfRef : (Delay ICEState -> Delay ICEState) -> Delay ICEState
selfRef step = step (Later (selfRef step))

||| iceFix: compute fixed point of ICE cycle with bounded fuel
iceFix : Int -> (ICEState -> ICEState) -> ICEState -> Maybe ICEState
iceFix fuel step init = runDelay fuel (selfRef stepper)
  where
    stepper : Delay ICEState -> Delay ICEState
    stepper prev = case runDelay fuel prev of
                        Just st => Now (step st)
                        Nothing => Now init

-- ============================================================
-- 3. ICE Corrector (L2 Rule Patching)
-- ============================================================

||| AnomalyKind: classification of ICE anomalies
data AnomalyKind : Type where
    Contradiction : AnomalyKind
    MisMatch      : AnomalyKind
    NoAnomaly     : AnomalyKind

||| DeltaPsi: anomaly signal
data DeltaPsi : Type where
    MkDeltaPsi : (kind : AnomalyKind)
              -> (focus : String)
              -> (magnitude : Double)
              -> DeltaPsi

||| Detect anomaly in current ICE state
detectAnomaly : ICEState -> DeltaPsi
detectAnomaly (MkICE rules (MkGraph nodes edges version) fixed) =
    if fixed then MkDeltaPsi NoAnomaly "" 0.0
    else case findContradiction rules of
              Just focus => MkDeltaPsi Contradiction focus 1.0
              Nothing    => case findMisMatch edges of
                                 Just focus => MkDeltaPsi MisMatch focus 0.5
                                 Nothing    => MkDeltaPsi NoAnomaly "" 0.0
  where
    findContradiction : List L2Rule -> Maybe String
    findContradiction [] = Nothing
    findContradiction (MkRule name _ concl _ :: rest) =
        if concl == "ABSURD" then Just name
        else findContradiction rest

    findMisMatch : List (String, String, Int, Int, String) -> Maybe String
    findMisMatch [] = Nothing
    findMisMatch ((src, dst, ps, pd, tag) :: rest) =
        if ps < 0 || pd < 0 then Just src
        else findMisMatch rest

||| iceCorrector: patch L2 rules based on anomaly
iceCorrector : DeltaPsi -> ICEState -> ICEState
iceCorrector (MkDeltaPsi Contradiction focus _) (MkICE rules graph _) =
    MkICE (patchRules focus rules) graph False
  where
    patchRules : String -> List L2Rule -> List L2Rule
    patchRules _ [] = []
    patchRules f (MkRule name prem concl tag :: rest) =
        if name == f
        then MkRule name prem ("CORRECTED_" ++ concl) "patched" :: rest
        else MkRule name prem concl tag :: patchRules f rest

iceCorrector (MkDeltaPsi MisMatch focus _) (MkICE rules (MkGraph nodes edges version) _) =
    MkICE rules (MkGraph nodes (fixPorts focus edges) version) False
  where
    fixPorts : String -> List (String, String, Int, Int, String) -> List (String, String, Int, Int, String)
    fixPorts _ [] = []
    fixPorts f ((src, dst, ps, pd, tag) :: rest) =
        if src == f
        then (src, dst, abs ps, abs pd, "rewired") :: rest
        else (src, dst, ps, pd, tag) :: fixPorts f rest

iceCorrector _ state = state

-- ============================================================
-- 4. Rewire Graph (L3 Beta-Rewire)
-- ============================================================

||| Beta-rewire the JinlingGraph topology based on anomaly
rewireGraph : DeltaPsi -> JinlingGraph -> JinlingGraph
rewireGraph (MkDeltaPsi Contradiction focus _) (MkGraph nodes edges version) =
    let newEdges = splitNode focus edges
    in MkGraph (focus :: nodes) newEdges (version + 1)
  where
    splitNode : String -> List (String, String, Int, Int, String) -> List (String, String, Int, Int, String)
    splitNode _ [] = []
    splitNode f ((src, dst, ps, pd, tag) :: rest) =
        if src == f
        then (src ++ "_a", dst, ps, pd, tag) ::
             (src ++ "_b", dst, ps + 1, pd, "split") ::
             splitNode f rest
        else (src, dst, ps, pd, tag) :: splitNode f rest

rewireGraph (MkDeltaPsi MisMatch focus _) (MkGraph nodes edges version) =
    MkGraph nodes (rewirePorts focus edges) (version + 1)
  where
    rewirePorts : String -> List (String, String, Int, Int, String) -> List (String, String, Int, Int, String)
    rewirePorts _ [] = []
    rewirePorts f ((src, dst, ps, pd, tag) :: rest) =
        if src == f
        then (dst, src, pd, ps, "beta_rewired") :: rewirePorts f rest
        else (src, dst, ps, pd, tag) :: rewirePorts f rest

rewireGraph _ g = g

-- ============================================================
-- 5. Step ICE (Top-Level Stepper)
-- ============================================================

||| Single step of the ICE cycle:
||| Detect anomaly -> Correct L2 rules -> Beta-rewire L3 graph -> Check convergence
stepICE : ICEState -> ICEState
stepICE state =
    let delta = detectAnomaly state
    in case delta of
            MkDeltaPsi NoAnomaly _ _ => recordFixed state
            _ => let corrected = iceCorrector delta state
                     regraphed = rewireGraph delta (getGraph corrected)
                 in setGraph regraphed corrected
  where
    getGraph : ICEState -> JinlingGraph
    getGraph (MkICE _ g _) = g

    setGraph : JinlingGraph -> ICEState -> ICEState
    setGraph newG (MkICE rules _ _) = MkICE rules newG False

    recordFixed : ICEState -> ICEState
    recordFixed (MkICE rules g _) = MkICE rules g True

||| Run ICE cycle to convergence (bounded)
runICE : Int -> ICEState -> ICEState
runICE 0 state = state
runICE fuel state =
    let next = stepICE state
    in case getFixed next of
            True  => next
            False => runICE (fuel - 1) next
  where
    getFixed : ICEState -> Bool
    getFixed (MkICE _ _ f) = f

-- ============================================================
-- 6. Serialization: iceToJson / gitDiff
-- ============================================================

||| Serialize an ICEState to a JSON-like string
iceToJson : ICEState -> String
iceToJson (MkICE rules (MkGraph nodes edges version) fixed) =
    "{\"rules\": [" ++ serializeRules rules ++ "], "
    ++ "\"graph\": {\"nodes\": [" ++ serializeNodes nodes ++ "], "
    ++ "\"edges\": [" ++ serializeEdges edges ++ "], "
    ++ "\"version\": " ++ show version ++ "}, "
    ++ "\"fixed\": " ++ (if fixed then "true" else "false") ++ "}"
  where
    serializeRules : List L2Rule -> String
    serializeRules [] = ""
    serializeRules [r] = serializeRule r
    serializeRules (r :: rs) = serializeRule r ++ ", " ++ serializeRules rs

    serializeRule : L2Rule -> String
    serializeRule (MkRule name prem concl tag) =
        "{\"name\": \"" ++ name ++ "\", \"conclusion\": \"" ++ concl
        ++ "\", \"tag\": \"" ++ tag ++ "\"}"

    serializeNodes : List String -> String
    serializeNodes [] = ""
    serializeNodes [n] = "\"" ++ n ++ "\""
    serializeNodes (n :: ns) = "\"" ++ n ++ "\", " ++ serializeNodes ns

    serializeEdges : List (String, String, Int, Int, String) -> String
    serializeEdges [] = ""
    serializeEdges [e] = serializeEdge e
    serializeEdges (e :: es) = serializeEdge e ++ ", " ++ serializeEdges es

    serializeEdge : (String, String, Int, Int, String) -> String
    serializeEdge (src, dst, ps, pd, tag) =
        "{\"src\": \"" ++ src ++ "\", \"dst\": \"" ++ dst
        ++ "\", \"port_src\": " ++ show ps ++ ", \"port_dst\": " ++ show pd
        ++ ", \"tag\": \"" ++ tag ++ "\"}"

||| Git-style diff between two ICE states
gitDiff : ICEState -> ICEState -> String
gitDiff before after =
    let (MkICE _ (MkGraph _ edgesB verB) _) = before
        (MkICE _ (MkGraph _ edgesA verA) _) = after
    in "--- version=" ++ show verB ++ "\n"
    ++ "+++ version=" ++ show verA ++ "\n"
    ++ diffEdges edgesB edgesA
  where
    diffEdges : List (String, String, Int, Int, String)
             -> List (String, String, Int, Int, String)
             -> String
    diffEdges [] [] = ""
    diffEdges [] ((src, dst, ps, pd, tag) :: rest) =
        "+ " ++ src ++ " -> " ++ dst ++ " [" ++ show ps ++ "," ++ show pd ++ "] " ++ tag ++ "\n"
        ++ diffEdges [] rest
    diffEdges ((src, dst, ps, pd, tag) :: rest) [] =
        "- " ++ src ++ " -> " ++ dst ++ " [" ++ show ps ++ "," ++ show pd ++ "] " ++ tag ++ "\n"
        ++ diffEdges rest []
    diffEdges (b :: bs) (a :: as) =
        let (srcB, dstB, psB, pdB, tagB) = b
            (srcA, dstA, psA, pdA, tagA) = a
        in (if srcB == srcA && dstB == dstA && psB == psA && pdB == pdA && tagB == tagA
            then "  " ++ srcB ++ " -> " ++ dstB ++ "\n"
            else "- " ++ srcB ++ " -> " ++ dstB ++ " [" ++ show psB ++ "," ++ show pdB ++ "] " ++ tagB ++ "\n"
              ++ "+ " ++ srcA ++ " -> " ++ dstA ++ " [" ++ show psA ++ "," ++ show pdA ++ "] " ++ tagA ++ "\n")
        ++ diffEdges bs as

-- ============================================================
-- 7. Main
-- ============================================================

||| Main entry point: demonstrate ICE self-referential cycle
main : IO ()
main = do
    -- Initial L2 rules with a contradiction
    let rules = [ MkRule "R1" ["A"] "B" "init"
                , MkRule "R2" ["B"] "ABSURD" "init"
                , MkRule "R3" ["C"] "D" "init"
                ]
    -- Initial graph
    let graph = MkGraph ["n1", "n2", "n3"]
                        [("n1", "n2", 0, 1, "link")
                        ,("n2", "n3", 1, 2, "link")
                        ,("n2", "n1", -1, 0, "bad_port")
                        ]
                        0
    let state = MkICE rules graph False

    putStrLn "=== M133 W1: Idris Self-Ref ICE Core ==="
    putStrLn ""
    putStrLn "Initial state:"
    putStrLn (iceToJson state)
    putStrLn ""

    -- Run ICE cycle
    let result = runICE 10 state
    putStrLn "After ICE convergence:"
    putStrLn (iceToJson result)
    putStrLn ""

    -- Show diff
    putStrLn "Git-style diff:"
    putStrLn (gitDiff state result)
    putStrLn ""
    putStrLn "=== Done ==="
