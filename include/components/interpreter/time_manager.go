package interpreter

import (
	"encoding/json"
	"fmt"
	"os"
	"time"
)

// TimeManager converts raw nsecs of kernel clock to datetime.
type TimeManager struct {
	RefWall int64
	RefMono int64
}

// NewTimeManager returns a new time-manager instance.
func NewTimeManager(referenceFilePath string) (*TimeManager, error) {
	data, err := os.ReadFile(referenceFilePath)
	if err != nil {
		return nil, fmt.Errorf("failed to open reference file `%s`: %v", referenceFilePath, err)
	}

	type RefTimes struct {
		RefWall float64 `json:"ref_wall"`
		RefMono float64 `json:"ref_mono"`
	}

	var rt RefTimes
	if err := json.Unmarshal(data, &rt); err != nil {
		return nil, fmt.Errorf("failed to parse reference file `%s`: %v", referenceFilePath, err)
	}

	return &TimeManager{
		RefWall: int64(rt.RefWall * 1e9),
		RefMono: int64(rt.RefMono * 1e9),
	}, nil
}

// ToTime accepts a nsecs and converts it to datetime.
func (t *TimeManager) ToTime(sec int64) time.Time {
	// delta from reference
	deltaNs := sec - t.RefMono

	// event wall time in nanoseconds
	eventWallNs := t.RefWall + deltaNs

	secs := eventWallNs / 1e9
	nsecs := eventWallNs % 1e9

	return time.Unix(secs, nsecs)
}
