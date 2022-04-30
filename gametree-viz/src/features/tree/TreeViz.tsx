import * as go from 'gojs';
import { ReactDiagram, DiagramProps } from 'gojs-react';
import styles from './Tree.module.css';

const GOJSSTYLES = {
  Diagram: {
    initialAutoScale: go.Diagram.UniformToFill,
    layout: new go.TreeLayout({ angle: 90, layerSpacing: 50 }),
    model: new go.TreeModel({
      isReadOnly: true, // don't allow the user to delete or copy nodes
    }),
  },
  Node: {
    Table: {
      Header: { row: 0, margin: new go.Margin(0, 24, 0, 2) },  // 展開ボタンのための余裕しろ
      ExpanderButton: { row: 0, alignment: go.Spot.TopRight },
      Content: { row: 1, visible: false },
    },
  },
  Link: {
    Link: { routing: go.Link.Orthogonal, selectable: false, corner: 10 },
    Shape: { strokeWidth: 1 },
    TextBlock: { segmentIndex: -2, background: "white" },
  },
};

const initDiagram = () => {
  const diagram = new go.Diagram(GOJSSTYLES.Diagram);

  diagram.nodeTemplate = new go.Node("Vertical")
    .add(new go.Panel("Table")
      .add(new go.TextBlock(GOJSSTYLES.Node.Table.Header)
        .bind("text", "key"))
      .add(go.GraphObject.make("PanelExpanderButton", "CONTENT", GOJSSTYLES.Node.Table.ExpanderButton))
      .add(new go.TextBlock({ name: "CONTENT", ...GOJSSTYLES.Node.Table.Content})
        .bind("text", "repr")))
    .add(go.GraphObject.make("TreeExpanderButton"));

  diagram.linkTemplate = new go.Link(GOJSSTYLES.Link.Link)
    .add(new go.Shape(GOJSSTYLES.Link.Shape)
      .bind("stroke", "edgeColor"))
    .add(new go.TextBlock(GOJSSTYLES.Link.TextBlock)
      .bind("text", "edgeRepr"));

  return diagram;
};

// export const TreeViz = (nodeDataArray: DiagramProps["nodeDataArray"]) => {
export const TreeViz = () => {
  return (
    <ReactDiagram
      initDiagram={initDiagram}
      divClassName={styles.diagramComponent}
      // nodeDataArray={nodeDataArray}
      nodeDataArray={[
        { key: 0, repr: "node 0\nnode0\nnode0" },
        { key: 1, parent: 0, repr: "node 1\nnode1\nnode1", edgeRepr: "edge 1", edgeTrun: "player", edgeColor: "DeepSkyBlue" },
        { key: 2, parent: 0, repr: "node 2\nnode2\nnode2", edgeRepr: "edge 2", edgeTrun: "player", edgeColor: "DeepSkyBlue" },
        { key: 3, parent: 2, repr: "node 3\nnode3\nnode3", edgeRepr: "edge 3", edgeTrun: "opponent", edgeColor: "red" },
        { key: 4, parent: 2, repr: "node 4\nnode4\nnode4", edgeRepr: "edge 4", edgeTrun: "opponent", edgeColor: "red" },
        { key: 5, parent: 2, repr: "node 5\nnode5\nnode5", edgeRepr: "edge 5", edgeTrun: "opponent", edgeColor: "red" },
      ]}
    />
  );
};
