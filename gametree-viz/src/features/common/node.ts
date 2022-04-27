export interface Node {
  id: number;
  repr: string;
  isTerminal: boolean;
  score: number | null;
  property: object;
  parentEdge: { // ts-interface-checker は循環定義を扱えないのでここで edge を定義 https://github.com/gristlabs/ts-interface-checker/issues/60
    turn: "player" | "opponent";
    property: object;
  } | null; // null: root node には parent edge はいない
  children: Node[];
}

// interface Edge {
//   id: number; // must be same as child.id
//   turn: "player" | "opponent";
//   property: object;
//   child: Node;
// }

// function instanceOfNode(data: any): data is Node {
//   return ("id" in data) &&
//     ("repr" in data) &&
//     ("isTerminal" in data) &&
//     ("score" in data) &&
//     ("property" in data) &&
//     ("children" in data) &&

//     (data.children instanceof Array);
// }

// function instanceOfEdge(data: any): data is Edge {
//   return ("id" in data) &&
//     ("turn" in data) &&
//     ("property" in data) &&
//     ("child" in data)
