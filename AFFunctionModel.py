import os
from typing import Any, Dict, Optional
import torch  # 用于判断是否可用 CUDA
from ultralytics import YOLO  # type: ignore


class CFunctionModel:
    """封装 Ultralytics YOLO 训练/推理/验证的轻量接口，带简易模型缓存。"""
    _model_cache: dict[str, YOLO] = {}
    def train(
        self,
        data_yaml_path: str,
        pretrained_model_path: str,
        project_dir: Optional[str] = None,
        run_name: str = "exp",
        epochs: int = 100,
        imgsz: int = 640,
        batch: int = 8,
        device: int | str = 0,
        workers: int = 4,
    ) -> Dict[str, Any]:
        model = self._get_model(pretrained_model_path)
        results = model.train(
            data=data_yaml_path,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            workers=workers,
            project=project_dir,
            name=run_name,
        )
        best_path = None
        try:
            best_path = results.best if hasattr(results, "best") else None
        except Exception:
            best_path = None
        return {"best": best_path, "project": project_dir, "name": run_name}

   

    def validate(
        self,
        model_path: str,
        data_yaml_path: str,
        imgsz: int = 640,
        device: int | str = 0,
    ) -> Dict[str, Any]:
        model = self._get_model(model_path)
        metrics = model.val(data=data_yaml_path, imgsz=imgsz, device=device)
        out: Dict[str, Any] = {}
        try:
            # 新版 ultralytics 的 metrics 為 dict-like；保守抽取常見 key
            out = {
                "metrics": getattr(metrics, "results_dict", dict(metrics)) if hasattr(metrics, "results_dict") else dict(metrics),
            }
        except Exception:
            out = {}
        return out

    # ----- internal helpers -----
    def _get_model(self, weights_path: str) -> YOLO:
        if weights_path in self._model_cache:
            return self._model_cache[weights_path]
        model = YOLO(weights_path)
        self._model_cache[weights_path] = model
        return model 
    
    # 通用预测（save 控制是否落盘，save_dir 存在时用于指定输出目录）
    def predict(
        self,
        model_path: str,
        source: str,
        save_dir: Optional[str] = None,
        save: bool = False,
        imgsz: int = 960,
        conf: float = 0.35,
        device: int | str = 0,
    ) -> Dict[str, Any]:
        # 若当前环境无 CUDA，则强制使用 CPU，避免 "Invalid CUDA device=0"
        try:
            if not torch.cuda.is_available():
                device = 'cpu'
        except Exception:
            device = 'cpu'

        model = self._get_model(model_path)
        project = None
        name = None
        if save and save_dir:
            project = os.path.dirname(save_dir)
            name = os.path.basename(save_dir)
        results = model.predict(
            source=source,
            save=save,
            imgsz=imgsz,
            conf=conf,
            device=device,
            project=project,
            name=name,
            retina_masks=True,
        )
        out: Dict[str, Any] = {"results": results}
        if save:
            out_dir = None
            try:
                out_dir = results[0].save_dir  # type: ignore[attr-defined]
            except Exception:
                out_dir = save_dir
            out["save_dir"] = str(out_dir) if out_dir else None
        return out
        
        # 推理
    def predict_no_save(
        self,
        model_path: str,
        source: str,
        imgsz: int = 960,
        conf: float = 0.35,
        device: int | str = 0,
    ) -> Dict[str, Any]:
        return self.predict(
            model_path=model_path,
            source=source,
            save=False,
            imgsz=imgsz,
            conf=conf,
            device=device,
        )

    # 保存可视化/标签
    def save_visualization(
        self,
        model_path: str,
        source: str,
        save_dir: str,
        imgsz: int = 960,
        conf: float = 0.35,
        device: int | str = 0,
    ) -> Dict[str, Any]:
        # 精确保存到指定目录 save_dir（不创建 runs/segment/... 子目录）
        os.makedirs(save_dir, exist_ok=True)
        # 先做不落盘的推理
        out = self.predict(
            model_path=model_path,
            source=source,
            save=False,
            imgsz=imgsz,
            conf=conf,
            device=device,
        )
        results_list = out.get("results", [])
        try:
            import cv2  # 延迟导入，避免无 GUI 环境报错
            from pathlib import Path
            import json
            for res in results_list:
                # 仅绘制框 + 类别文字：不显示置信度、不绘制分割掩码
                im = res.plot(conf=False, labels=True, masks=False)  # type: ignore[attr-defined]
                src_name = Path(getattr(res, 'path', 'pred.jpg')).name  # 原图名
                dst_path = str(Path(save_dir) / src_name)
                cv2.imwrite(dst_path, im)
                # ---- 组装并保存 JSON 标签 ----
                objects_json = []
                names_map = getattr(res, 'names', {}) or {}
                try:
                    boxes = res.boxes  # type: ignore[attr-defined]
                    xyxy = boxes.xyxy.cpu().tolist() if hasattr(boxes, 'xyxy') else []
                    clss = boxes.cls.int().cpu().tolist() if hasattr(boxes, 'cls') else []
                    confs = boxes.conf.cpu().tolist() if hasattr(boxes, 'conf') else []
                except Exception:
                    xyxy, clss, confs = [], [], []

                polygons = None
                try:
                    if getattr(res, 'masks', None) is not None and hasattr(res.masks, 'xy'):
                        polygons = [p.tolist() for p in res.masks.xy]
                except Exception:
                    polygons = None

                num_obj = max(len(xyxy), len(clss), len(confs), len(polygons or []))
                for i in range(num_obj):
                    cid = clss[i] if i < len(clss) else None
                    cname = names_map.get(int(cid), None) if cid is not None else None
                    obj = {
                        "class_id": cid,
                        "class_name": cname,
                        "confidence": confs[i] if i < len(confs) else None,
                        "box_xyxy": xyxy[i] if i < len(xyxy) else None,
                    }
                    if polygons is not None and i < len(polygons):
                        obj["polygon"] = polygons[i]
                    objects_json.append(obj)

                meta = {
                    "image": src_name,
                    "save_path": dst_path,
                    "objects": objects_json,
                }
                json_path = str(Path(save_dir) / (Path(src_name).stem + '.json'))
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(meta, f, ensure_ascii=False)
            out["save_dir"] = save_dir
        except Exception:
            # 如果自保存失败，回退到框架自带保存
            fallback = self.predict(
                model_path=model_path,
                source=source,
                save_dir=save_dir,
                save=True,
                imgsz=imgsz,
                conf=conf,
                device=device,
            )
            # 覆盖一次保存结果，移除可视化中的置信度数值
            try:
                import cv2  # 延迟导入
                from pathlib import Path
                for res in fallback.get("results", []):
                    im = res.plot(conf=False, labels=True, masks=False)  # type: ignore[attr-defined]
                    src_name = Path(getattr(res, 'path', 'pred.jpg')).name
                    dst_path = str(Path(save_dir) / src_name)
                    cv2.imwrite(dst_path, im)
            except Exception:
                pass
            out = fallback
        return out
