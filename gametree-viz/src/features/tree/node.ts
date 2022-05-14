export interface Node {
  id: string;
  repr: string;
  isTerminal: boolean;
  isRational: boolean;
  properties: object;
  parentEdge: { // ts-interface-checker は循環定義を扱えないのでここで edge を定義 https://github.com/gristlabs/ts-interface-checker/issues/60
    id: string;
    repr: string;
    turn: "player" | "opponent";
    isRational: boolean;
    properties: object;
  } | null; // null: root node には parent edge はいない
  children: Node[];
}
