import * as go from 'gojs';
import { ReactDiagram } from 'gojs-react';
import styles from './treeDataViz.module.css';


const gojsStyles = {
  Diagram: {
    TreeLayout: { angle: 90, layerSpacing: 50 },
  },
  Node: {
    Shape: { fill: "#1F4963", stroke: null },
    TextBlock: { font: "bold 13px Helvetica, bold Arial, sans-serif", stroke: "white", margin: 3 },
  },
  Link: {
    Shape: { strokeWidth: 1 },
  },
};

function initDiagram() {
  const diagram = new go.Diagram(
    {
      initialAutoScale: go.Diagram.UniformToFill,
      layout: new go.TreeLayout(gojsStyles.Diagram.TreeLayout),
      model: new go.TreeModel({
        isReadOnly: true, // don't allow the user to delete or copy nodes
      }),
    }
  );

  diagram.nodeTemplate = new go.Node("Vertical")
    .add(new go.Panel("Table")
      .add(new go.TextBlock({ row: 0, margin: new go.Margin(0 ,24, 0, 2) })
        .bind("text", "key"))
      .add(go.GraphObject.make("PanelExpanderButton", "CONTENT", { row: 0, alignment: go.Spot.TopRight }))
      .add(new go.TextBlock({ name: "CONTENT", row: 1, visible: false })
        .bind("text", "repr")))
    .add(go.GraphObject.make("TreeExpanderButton"));

  diagram.linkTemplate = new go.Link({ routing: go.Link.Orthogonal, selectable: false, corner: 10 })
    .add(new go.Shape(gojsStyles.Link.Shape).bind("stroke", "edgeColor"))
    .add(new go.TextBlock({ segmentIndex: -2, background: "white" })
      .bind("text", "edgeRepr"));

  return diagram;
}

// function handleModelChange(changes: any) {
//   alert('GoJS model changed!');
// }

export const TreeDataViz = () => {
  return (
    <ReactDiagram
      initDiagram={initDiagram}
      divClassName={styles.diagramComponent}
      nodeDataArray={[
        { key: 0, repr: "node 0\nnode0\nnode0" },
        { key: 1, parent: 0, repr: "node 1\nnode1\nnode1", edgeRepr: "edge 1", edgeTrun: "player", edgeColor: "DeepSkyBlue" },
        { key: 2, parent: 0, repr: "node 2\nnode2\nnode2", edgeRepr: "edge 2", edgeTrun: "player", edgeColor: "DeepSkyBlue" },
        { key: 3, parent: 2, repr: "node 3\nnode3\nnode3", edgeRepr: "edge 3", edgeTrun: "opponent", edgeColor: "red" },
        { key: 4, parent: 2, repr: "node 4\nnode4\nnode4", edgeRepr: "edge 4", edgeTrun: "opponent", edgeColor: "red" },
        { key: 5, parent: 2, repr: "node 5\nnode5\nnode5", edgeRepr: "edge 5", edgeTrun: "opponent", edgeColor: "red" },
      ]}
      // onModelChange={handleModelChange}
    />
  );
};
