import { Node } from "./node";
import nodeTI from "./node-ti";
import { CheckerT, createCheckers } from "ts-interface-checker";
import fooTI from "./foo-ti";
import { Square as sq} from "./foo";

const { Square } = createCheckers(fooTI) as {Square: CheckerT<sq>};

// const data = {size: 1};
// if (Square.test(data)) {
//   data;
// }
// Square.check({size: 1});
// Square.check({size: 1, color: "green"});  // OK
// Square.check({color: "green"});           // Fails with "value.size is missing"
// Square.check({size: 4, color: 5});        // Fails with "value.color is not a string"

const nodeChecker = createCheckers(nodeTI) as { Node: CheckerT<Node> };
// const { Edge } = createCheckers(EdgeIT);

// Node.check({a: 10});

export const parseNode = (nodeData: object) => {
  // nodeData.id;
  // Node.strictCheck(nodeData);
  if (nodeChecker.Node.strictTest(nodeData)) {
    return nodeData;
    // console.log(nodeData.id);
  };
  // Node.strictTest(nodeData);
  try {
    nodeChecker.Node.strictCheck(nodeData);
  } catch (error) {
    console.log(error);
  }
  console.log("parse Error log");
  throw Error("parse Error throw");
  // if (Node.strictTest(nodeData)) {
  //   const node: Node = {
  //     id: nodeData.id,
  //     repr: nodeData.repr,
  //     isTerminal: nodeData.isTerminal,
  //     score: nodeData.score,
  //     property: nodeData.property,
  //     children: nodeData.children.map(parseEdge),
  //   };
  //   return node;
  // }
};

const parseEdge = (edgeData: object) => {
  // Edge.strictCheck(edgeData);
  return edgeData;
  // const edge: Edge = {
  //   id: edgeData.id,
  //   turn: edgeData.turn,
  //   property: edgeData.property,
  //   child: parseNode(edgeData.child),
  // };
  // return edge;
};
