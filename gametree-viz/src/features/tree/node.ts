export interface Node {
  id: number;
  repr: string;
  isTerminal: boolean;
  score: number | null;
  property: object;
  parentEdge: { // ts-interface-checker は循環定義を扱えないのでここで edge を定義 https://github.com/gristlabs/ts-interface-checker/issues/60
    id: number;
    repr: string;
    turn: "player" | "opponent";
    property: object;
  } | null; // null: root node には parent edge はいない
  children: Node[];
}
