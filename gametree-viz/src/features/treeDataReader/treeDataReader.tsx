import React, { ChangeEvent, useState } from 'react';

import { useAppSelector, useAppDispatch } from '../../app/hooks';
import {
  selectData,
  setData,
  readSingleFileAsync,
} from './treeDataReaderSlice';
// import styles from './FileReader.module.css';


const revealFileFromEvent = (event: ChangeEvent<HTMLInputElement>) => {
  if (!event.target.files) {
    throw Error('event.target.files is null');
  }
  const file = event.target.files[0];
  if (!file) {
    throw Error('file is null');
  }
  return file;
}

export function TreeDataReader() {
  const dispatch = useAppDispatch();
  const fileContent = useAppSelector(selectData);

  return (
      <div>
        <input type="file" onChange={(e) => dispatch(readSingleFileAsync(revealFileFromEvent(e)))}/>
        <p>{JSON.stringify(fileContent)}</p>
    </div>
  );
}