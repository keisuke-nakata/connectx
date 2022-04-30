import { useAppSelector, useAppDispatch } from '../../app/hooks';
import {
  selectData,
  readSingleFileAsync,
  selectReadMsg,
} from './treeSlice';
// import styles from './FileReader.module.css';

export const TreeDataReader = () => {
  const dispatch = useAppDispatch();

  const readMsg = useAppSelector(selectReadMsg);
  // const fileContent = useAppSelector(selectData);

  return (
      <div>
        <input type="file" onChange={(e) => dispatch(readSingleFileAsync(e))}/>
        <p>{readMsg}</p>
        {/* <p>{JSON.stringify(fileContent)}</p> */}
    </div>
  );
};
