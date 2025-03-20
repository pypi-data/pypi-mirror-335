// copied from https://gist.github.com/wojtekmaj/da7fb5908cf30a9a91a1243c663dea91
import React, { use as originalUse, useContext } from 'react';

const STATUS = {
  PENDING: 'pending',
  REJECTED: 'rejected',
  FULFILLED: 'fulfilled',
} as const;

type TState<T> =
  | { status: typeof STATUS.PENDING; promise: Promise<void> }
  | { status: typeof STATUS.REJECTED; error: Error }
  | { status: typeof STATUS.FULFILLED; result: T };

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const states = new Map<Promise<unknown>, TState<any>>();

function usePromiseFallback<T>(usable: Promise<T>): T {
  const existingState = states.get(usable);

  const state: TState<T> =
    existingState ||
    (() => {
      const promise = usable
        .then((data) => {
          states.set(usable, {
            status: STATUS.FULFILLED,
            result: data,
          });
        })
        .catch((error) => {
          states.set(usable, {
            status: STATUS.REJECTED,
            error,
          });
        });

      const newState: TState<T> = { status: 'pending', promise: promise };
      states.set(usable, newState);
      return newState;
    })();

  switch (state.status) {
    case STATUS.PENDING:
      // Suspend the component while fetching
      throw state.promise;
    case STATUS.REJECTED:
      // Result is an error
      throw state.error;
    case STATUS.FULFILLED:
      // Result is a fulfilled promise
      return state.result;
  }
}

function useContextFallback<T>(context: React.Context<T>) {
  return useContext(context);
}

function useFallback<T>(usable: Promise<T> | React.Context<T>): T {
  if (usable.then) {
    // eslint-disable-next-line react-hooks/rules-of-hooks
    return usePromiseFallback(usable);
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  return useContextFallback(usable);
}

const use = originalUse || useFallback;

export default use;